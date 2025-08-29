## 本番環境で動作確認方法
### 事前準備
1. main or main-testブランチにdevelopブランチをマージ 

### 環境構築
1. Actionsタブを開き、Terraform Apply (on main)とTerraform Destroy (manual)のworkflow runsを見て、\
   実行中のworkflow runがないことを確認後、下図①-③を実施。**ブランチはmain or main-testにすること**。\
   AWS上にインフラ環境が構築される（5分くらいかかる）。\
   他の人がすで構築済みの場合は、エラーになる。その場合、他の人が後述するterraform destroy後に再度実行。
 
<img width="1672" height="587" alt="Image" src="https://github.com/user-attachments/assets/8892c568-583f-495b-b441-93460ab74fb0" />

2. 対象のworkflow runが正常に終了し、**数分後**（コンテナが起動後）、\
   [https://voucherz.jp](https://voucherz.jp) にアクセスし、動作確認。


### 環境の削除
1. テスト実施後は速やかに環境を削除してください。（節約のために）\
   下図①-③を実施。**ブランチはmain or main-testにすること。**\
   AWS上のインフラ環境が削除される（5分くらいかかる）。

<img width="1672" height="587" alt="Image" src="https://github.com/user-attachments/assets/9c06437a-7a06-49f9-a1e3-124add20a3eb" />

