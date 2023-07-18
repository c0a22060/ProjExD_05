# 勇者こうかとん
## 実行環境の必要条件
* python >= 3.10
* pygame >= 2.1

## ゲームの概要
主人公キャラクターこうかとんがUFOの親玉と戦う

## ゲームの実装
###共通基本機能
* 壁の判定を確認する関数
* こうかとんの方角を確認する関数
* 主人公キャラクターに関するクラス
* 爆弾に関するクラス
* 爆発に関するクラス
* 敵に関するクラス
* スコアに関するクラス

### 担当追加機能
* 敵に関するクラス
### ToDo
class BOSS 一定数の敵を倒したら新しい敵の実装
imgs = pg.image.load(f"ProjExd_05/fig/UFO_BOSS.png")（画像の読み込み）
self.hp = 3（このクラス内での敵のhpの実装）
if self.hp == 0:　（敵のhpがゼロになったら）
for emy in pg.sprite.groupcollide(emys, beams, True, True).keys():
            exps.add(Explosion(emy, 100))  # 爆発エフェクト
            score.score_up(10)  # 10点アップ
            bird.change_img(6, screen)  # こうかとん喜びエフェクト
            ten+=1　　　（敵を倒したら変数に＋１）
if ten%2 == 0 and ten != 0:  （％2の部分に何体倒したらボスが出るかの数）
            bosses.add(BOSS())
            ten+=1（ボスを倒しても次に出てくるまでの数にカウントされる）
### メモ
* クラス内の変数は，すべて，「get_変数名」という名前のメソッドを介してアクセスするように設計してある
* すべてのクラスに関係する関数は，クラスの外で定義してある
