import math
import random
import sys
import time
import pygame as pg
WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ



def check_bound(obj: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内か画面外かを判定し，真理値タプルを返す
    引数 obj：オブジェクト（爆弾，こうかとん，ビーム）SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj.left < 0 or WIDTH < obj.right:  # 横方向のはみ出し判定
        yoko = False
    if obj.top < 0 or HEIGHT < obj.bottom:  # 縦方向のはみ出し判定
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    orgから見て，dstがどこにあるかを計算し，方向ベクトルをタプルで返す
    引数1 org：爆弾SurfaceのRect
    引数2 dst：こうかとんSurfaceのRect
    戻り値：orgから見たdstの方向ベクトルを表すタプル
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm


class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"ex05/fig/{num}.png"), 0, 1.5)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 1.0),  # 右下
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10
        self.state = "nomal"
        self.max_hp = 3  # 最大HP
        self.hp = self.max_hp  # 現在のHP

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"ex05/fig/{num}.png"), 0, 2.0)
        screen.blit(self.image, self.rect)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                self.rect.move_ip(+self.speed*mv[0], +self.speed*mv[1])
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        if check_bound(self.rect) != (True, True):
            for k, mv in __class__.delta.items():
                if key_lst[k]:
                    self.rect.move_ip(-self.speed*mv[0], -self.speed*mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]
        screen.blit(self.image, self.rect)
    

    def get_direction(self) -> tuple[int, int]:
        return self.dire

    def decrease_hp(self):
        self.hp -= 1

    def is_dead(self) -> bool:
        return self.hp <= 0


class Bomb(pg.sprite.Sprite):
    """
    爆弾に関するクラス
    """
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

    def __init__(self, emy: "Enemy", bird: Bird):
        """
        爆弾円Surfaceを生成する
        引数1 emy：爆弾を投下する敵機
        引数2 bird：攻撃対象のこうかとん
        """
        super().__init__()
        rad = 10  # 爆弾円の半径：10以上50以下の乱数
        color = random.choice(__class__.colors)  # 爆弾円の色：クラス変数からランダム選択
        self.image = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        # 爆弾を投下するemyから見た攻撃対象のbirdの方向を計算
        self.vx, self.vy = calc_orientation(emy.rect, bird.rect)
        self.rect.centerx = emy.rect.centerx
        self.rect.centery = emy.rect.centery+emy.rect.height/2
        self.speed = 6

    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if check_bound(self.rect) == (False, True):
            self.vx *= -1
        if check_bound(self.rect) == (True, False):
            self.vy *= -1


class Beam(pg.sprite.Sprite):
    """
    ビームに関するクラス
    """
    def __init__(self, bird: Bird):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん
        """
        super().__init__()
        self.vx, self.vy = bird.get_direction()
        angle = math.degrees(math.atan2(-self.vy, self.vx))
        self.image = pg.transform.rotozoom(pg.image.load(f"ex05/fig/beam.png"), angle, 1.5)
        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
        self.rect = self.image.get_rect()
        self.rect.centery = bird.rect.centery+bird.rect.height*self.vy
        self.rect.centerx = bird.rect.centerx+bird.rect.width*self.vx
        self.speed = 10

    def update(self):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            
            self.kill()

class Sword(pg.sprite.Sprite):
    """
    剣に関するクラス
    """
    def __init__(self, bird: Bird, life: int):
        """
        剣画像surfaceを生成する
        引数1 bird: 剣を振るこうかとん
        引数2 life: 剣をしまう時間
        """
        super().__init__()
        self.vx, self.vy = bird.get_direction()
        angle = math.degrees(math.atan2(-self.vy, self.vx))
        self.image = pg.transform.rotozoom(pg.image.load("ex05/fig/sword-3.png"), angle, 0.4)
        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
        self.rect = self.image.get_rect()
        self.rect.centery = bird.rect.centery+bird.rect.height*self.vy
        self.rect.centerx = bird.rect.centerx+bird.rect.width*self.vx
        self.life=life
    def update(self,bird: Bird):
        """
        剣をこうかとんの移動量に合わせて移動させる
        時間がたったら剣をしまうようにする
        引数1 bird: 剣の向き
        """
        self.rect.centery = bird.rect.centery+bird.rect.height*self.vy
        self.rect.centerx = bird.rect.centerx+bird.rect.width*self.vx
        self.life -= 1
        if self.life < 0:
            self.kill()



class Explosion(pg.sprite.Sprite):
    """
    爆発に関するクラス
    """
    def __init__(self, obj: "Bomb|Enemy", life: int):
        """
        爆弾が爆発するエフェクトを生成する
        引数1 obj：爆発するBombまたは敵機インスタンス
        引数2 life：爆発時間
        """
        super().__init__()
        img = pg.image.load("ex05/fig/explosion.gif")
        self.imgs = [img, pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life

    def update(self):
        """
        爆発時間を1減算した爆発経過時間_lifeに応じて爆発画像を切り替えることで
        爆発エフェクトを表現する
        """
        self.life -= 1
        self.image = self.imgs[self.life//10%2]
        if self.life < 0:
            self.kill()


class Enemy(pg.sprite.Sprite):
    """
    敵機に関するクラス
    """
    imgs = [pg.image.load(f"ex05/fig/alien{i}.png") for i in range(1, 4)]
    
    def __init__(self):
        super().__init__()
        self.image = random.choice(__class__.imgs)
        self.rect = self.image.get_rect()
        self.rect.center = random.randint(50, WIDTH-50), 0
        self.vy = +6
        self.bound = random.randint(20, HEIGHT-20)  # 停止位置
        self.state = "down"  # 降下状態or停止状態
        self.interval = random.randint(50, 300)  # 爆弾投下インターバル

    def update(self):
        """
        敵機を速度ベクトルself.vyに基づき移動（降下）させる
        ランダムに決めた停止位置_boundまで降下したら，_stateを停止状態に変更する
        引数 screen：画面Surface
        """
        if self.rect.centery > self.bound:
            self.vy = 0
            self.state = "stop"
        self.rect.centery += self.vy
        

class BOSS(pg.sprite.Sprite):
    def __init__(self):
        imgs = pg.image.load(f"ex05/fig/UFO_BOSS.png")
        imgs = pg.transform.scale(imgs,(150,150))
        super().__init__()
        self.hp = 2
        self.image = imgs
        self.rect = self.image.get_rect()
        self.rect.center = random.randint(0, WIDTH), 0
        self.vy = +6
        self.bound = random.randint(50, HEIGHT/2) 
        self.state = "down"  
        self.interval = random.randint(50, 300)
        self.move = 3
        self.move_sum = 0
    def update(self):
        if self.rect.centery > self.bound:
            self.vy = 0
            self.state = "stop"
        self.rect.centery += self.vy
        if self.hp == 0:
            self.kill()
        if self.state == "stop":
            self.rect.centery += self.move
            self.move_sum += self.move
        if self.move_sum >= 150:
            self.move = -3
            self.move_sum = 0
        if self.move_sum <= -150:
            self.move = 3
            self.move_sum = 0
        
            
    def hp_set(self, num):
        self.hp += num



class Score:
    """
    打ち落とした爆弾，敵機の数をスコアとして表示するクラス
    爆弾：1点
    敵機：10点
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.score = 0
        self.image = self.font.render(f"Score: {self.score}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-50

    def score_up(self, add):
        self.score += add

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Score: {self.score}", 0, self.color)
        screen.blit(self.image, self.rect)


class HPBar:
    """
    HPバーを表示するクラス
    """
    def __init__(self, bird: Bird):
        self.bird = bird
        self.max_width = 200  # HPバーの最大幅
        self.height = 20  # HPバーの高さ
        self.rect = pg.Rect((100, 50, self.max_width, self.height))
        self.color = (0, 0, 255)  # HPバーの色

    def update(self, screen: pg.Surface):
        hp_ratio = self.bird.hp / self.bird.max_hp
        width = int(self.max_width * hp_ratio)
        self.rect.width = width
        pg.draw.rect(screen, self.color, self.rect)


class Point(pg.sprite.Sprite):
    def __init__(self, obj: "Bomb|Enemy", life: int, size):
        """
        相手からポイントを落とす関数
        """
        super().__init__()
        img = pg.transform.rotozoom(pg.image.load("ex05/fig/food_yakitori.png"), 0, size)
        self.imgs = [img, pg.transform.flip(img, 1, 0)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life

    def update(self):
        self.life += 1
        self.image = self.imgs[self.life//50%2]


class Shield(pg.sprite.Sprite):
    """
    盾に関するクラス
    """
    def __init__(self, bird: Bird):
        """
        重力球のSurfaceを生成する
        引数1 xy：こうかとんの座標
        """
        super().__init__()
        imge3 = pg.transform.rotozoom(pg.image.load(f"ex05/fig/shield.png"), 0, 0.3)
        imge2 = pg.transform.rotozoom(pg.image.load(f"ex05/fig/shield2.png"), 0, 0.3)
        imge1 = pg.transform.rotozoom(pg.image.load(f"ex05/fig/shield3.png"), 0, 0.3)
        self.images = [imge1, imge1, imge2, imge3]
        self.image = pg.transform.rotozoom(pg.image.load(f"ex05/fig/shield2.png"), 0, 0.3)
        self.rect = self.image.get_rect()
        self.rect.center = bird.rect.center
        self.life = 3

    def update(self):
        """
        重力球のライフを減少させる
        引数 screen：画面Surface
        """
        self.image = self.images[self.life]
        if self.life <= 0:
            self.kill()

    def life_change(self , num):
        self.life -= num


class Difficult:
    """
    時間に応じて難易度を表示する関数
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (255, 0, 0)
        self.difficulty = 0
        self.image = self.font.render(f"Level: {self.difficulty}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-90

    def difficult_up(self, add):
        self.difficulty += add

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Level: {self.difficulty}", 0, self.color)
        screen.blit(self.image, self.rect)


class Cooltime:
    """
    射撃のクールタイム表示
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.colors = [(255, 0, 0), (255, 255, 0), (0, 255, 0)]
        self.color = self.colors[2]
        self.cooltime = 0
        self.rect = 0, 0
        self.view = -100

    def star_ct(self):
        self.cooltime = 1

    def update(self, screen: pg.Surface, tmr, bird: Bird):
        """
        時間によって形と色が変わる四角形を表示する.
        """
        self.rectx, self.recty = bird.rect.bottomleft
        self.recty += 10
        if self.cooltime >= 1:
            self.cooltime += 1
            if self.cooltime <= 20:
                self.color = self.colors[0]
                pg.draw.rect(screen, self.color, (self.rectx, self.recty, self.cooltime, 5))
            elif self.cooltime > 20:
                self.color = self.colors[1]
                pg.draw.rect(screen, self.color, (self.rectx, self.recty, self.cooltime, 5))
        if self.view + 50 >= tmr and Cooltime ==0:
            self.color = self.colors[2]
            pg.draw.rect(screen, self.color, (self.rectx, self.recty, 60, 5))
        if self.cooltime >= 50:
            self.cooltime = 0
            self.view = tmr
        

class Achievement:
    """
    実績機能
    """
    def __init__(self):
        self.score = 0
        self.shot = 0
        self.block = 0
        self.shield = 1

    def score_up(self):
        self.score += 1
        self.shot += 1
        self.block += 1

    def update(self, screen: pg.Surface):
        if self.score >= 500:
            print("すごい")


class Shiled_count:
    """
    シールドの個数を表示する
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 0)
        self.count = 0
        self.shiled = pg.transform.rotozoom(pg.image.load(f"ex05/fig/shield.png"), 0, 0.2)
        self.rect2 = self.shiled.get_rect()
        self.rect2.center = WIDTH-80, HEIGHT-60
        self.image = self.font.render(f"{self.count}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = WIDTH-80, HEIGHT-60

    def update(self, screen: pg.Surface, score, use):
        screen.blit(self.shiled, self.rect2)
        self.count = score // use
        self.image = self.font.render(f"{score // use // 5}", 0, self.color)
        screen.blit(self.image, self.rect)



class Title(pg.sprite.Sprite):
    def __init__(self):
        self.img = pg.image.load("ex05/fig/fire.jpg") 
        self.fonthk = pg.font.Font(None, 200)
        self.texthk = self.fonthk.render("HERO KOKATON", True, (0,255, 255))
        self.recthk = self.texthk.get_rect(center=(WIDTH // 2, HEIGHT // 2 ))
        self.fontpe = pg.font.Font(None, 80)
        self.textpe = self.fontpe.render("Press Enter to Start ...", True, (0, 200, 0))
        self.rectpe = self.textpe.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 200))
        

    def update(self, screen: pg.Surface):
        screen.blit(self.img, [0, 0])
        screen.blit(self.texthk, self.recthk)
        screen.blit(self.textpe, self.rectpe)


def main():
    ten=0
    pg.display.set_caption("勇者こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("ex05/fig/pg_bg.jpg")
    """
    追加機能(タイトル表示)
    タイトル画面に"HERO KOKATON"と"Press Enter to Start"を表示
    """
    
    
    score = Score()
    title = Title()
    bg_img = pg.image.load("ex04/fig/pg_bg.jpg")
    bg_img2 = pg.transform.flip(bg_img, 1, 0)
    score = Score()
    difficult = Difficult()
    cooltime = Cooltime()
    achievement = Achievement()
    shield_count = Shiled_count()

    bird = Bird(3, (900, 400))
    hp_bar = HPBar(bird)
    bombs = pg.sprite.Group()
    beams = pg.sprite.Group()
    swords=pg.sprite.Group()
    exps = pg.sprite.Group()
    emys = pg.sprite.Group()
    bosses = pg.sprite.Group()
    points = pg.sprite.Group()
    shields = pg.sprite.Group()


    
    tmr = 0
    x = 0
    clock = pg.time.Clock()
    running = True
    
    while running:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                running = False
        title.update(screen)
        pg.display.update()
    
    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE and cooltime.cooltime == 0:
                beams.add(Beam(bird))
                cooltime.star_ct()
            if event.type == pg.KEYDOWN and event.key == pg.K_LSHIFT:
                swords.add(Sword(bird, 10))   
            if event.type == pg.KEYDOWN and event.key == pg.K_TAB and achievement.score // achievement.shield >= 5:
                shields.add(Shield(bird))
                achievement.shield += 1

        screen.blit(bg_img2, [1600 -x, 0])
        screen.blit(bg_img, [3199 -x, 0])
        screen.blit(bg_img, [-x, 0])
            
        if ten%2 == 0 and ten != 0:
            bosses.add(BOSS())
            ten+=1
            
        for boss in bosses:
            if boss.state == "stop" and tmr%emy.interval == 0:
                # 敵機が停止状態に入ったら，intervalに応じて爆弾投下
                
                bombs.add(Bomb(boss, bird))
                #Bomb.bomb_size(10)
        
        if tmr%200 == 0:
            emys.add(Enemy())
        if tmr+100 %200 == 0 and difficult.difficulty >= 5:
            emys.add(Enemy())
        if tmr%1000 == 0 and difficult.difficulty < 10:
            difficult.difficult_up(1)

        for emy in emys:
            if emy.state == "stop" and tmr % emy.interval == 0:
                # 敵機が停止状態に入ったら，intervalに応じて爆弾投下                    
                bombs.add(Bomb(emy, bird))
                

        for emy in pg.sprite.groupcollide(emys, beams, True, True).keys():
            exps.add(Explosion(emy, 100))  # 爆発エフェクト
            points.add(Point(emy, 0, 0.2))
            bird.change_img(6, screen)  # こうかとん喜びエフェクト
            ten+=1
            achievement.score += 1
        
        for boss in pg.sprite.groupcollide(bosses, beams, False, True).keys():
            boss.hp_set(-1)
            exps.add(Explosion(boss, 100))
            achievement.score += 1
            points.add(Point(boss, 0, 0.2))

        for bomb in pg.sprite.groupcollide(bombs, beams, True, True).keys():
            exps.add(Explosion(bomb, 100))  # 爆発エフェクト

        for emy in pg.sprite.groupcollide(emys, swords, True, False).keys():
            exps.add(Explosion(emy, 100))  # 爆発エフェクト
            points.add(Point(emy, 0, 0.2))
            achievement.score += 1
        for bomb in pg.sprite.groupcollide(bombs, swords,True, False).keys():
            exps.add(Explosion(bomb, 50))  # 爆発エフェクト
            
        for boss in pg.sprite.groupcollide(bosses, swords, False, True).keys():
            boss.hp_set(-1)
            exps.add(Explosion(boss, 100))
            achievement.score += 1
        
        if len(pg.sprite.spritecollide(bird, points, True)) != 0:
            score.score_up(10)  # 10点アップ
            
        if len(pg.sprite.spritecollide(bird, bombs, True)) != 0:
            bird.decrease_hp()
            if bird.is_dead():
                bird.change_img(8, screen)  # こうかとん悲しみエフェクト
                score.update(screen)
                pg.display.update()
                time.sleep(2)
                return

        
        for shield in pg.sprite.groupcollide(shields, bombs, False, True).keys():
            Shield.life_change(shield, 1)
        
        
        bird.update(key_lst, screen)
        hp_bar.update(screen)
        beams.update()
        beams.draw(screen)
        swords.update(bird)
        swords.draw(screen)
        emys.update()
        emys.draw(screen)
        bosses.update()
        bosses.draw(screen)
        bombs.update()
        bombs.draw(screen)
        points.update()
        points.draw(screen)
        exps.update()
        exps.draw(screen)
        score.update(screen)
        shield_count.update(screen, achievement.score, achievement.shield)
        difficult.update(screen)
        cooltime.update(screen, tmr, bird)
        shields.update()
        shields.draw(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)
            
            
        x += 1
        
        if x > 3199:
            x = 0


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()