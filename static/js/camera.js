const startBtn = document.getElementById('start-qr');
const startGuide = document.getElementById('start-guide');
const frame = document.getElementById('frame');
const closeBtn = document.getElementById('close-qr');
const video  = document.getElementById('video');

let stream;
startBtn.addEventListener('click', async () => {
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            audio: false,
            video: {facingMode: {exact: 'environment'}}
        });
    } catch (err1) {
        try {
            stream = await navigator.mediaDevices.getUserMedia({
                audio: false,
                video: {facingMode: {exact: 'user'}}
            });
        } catch (err2) {
            try {
                stream = await navigator.mediaDevices.getUserMedia({
                    audio: false,
                    video: true
                });
            } catch (err3) {
                alert('カメラが起動できませんでした');
                return;
            }
        }
    }

    video.srcObject = stream;
    await video.play();
    checkImage();
    startBtn.style.display = 'none';
    startGuide.style.display = 'none';
    closeBtn.style.display = 'block';
    frame.style.display = 'block';
});

closeBtn.addEventListener('click', () => {
    if (stream) {
        const tracks = stream.getTracks().forEach(track => track.stop());
    }
    
    video.srcObject = null;
    startBtn.style.display = 'block';
    startGuide.style.display = 'block';
    closeBtn.style.display = 'none';
    frame.style.display = 'none';
});
    

const canvas = document.querySelector('#canvas');
const ctx = canvas.getContext('2d');

let qr_check = false;
const checkImage = () => {
    // 取得している動画をCanvasに描画
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Canvasからデータを取得
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);

    // jsQRに渡す
    const code = jsQR(imageData.data, canvas.width, canvas.height);

    // QRコードの読み取りに成功したら値を出力
    // 失敗したら再度実行
    if (!qr_check && code) {
        console.log("QRcodeが見つかりました", code); // デバッグ用
        qr_check = true;
        // バックへ非同期処理
        
    } else {
        console.log("失敗。0.5秒後に再トライ"); // デバッグ用
        qr_check = false;
        setTimeout(() => { checkImage() }, 500);
    }
};




// ・html
// カメラ枠を用意
// 枠内に、カメラ映像・canvas・カメラボタンを配置
// ・css
// 三つをwrapperで、relative,absoluteする
// ・js
// カメラボタンidを取得
// カメラ映像idを取得
// カメラボタンidが発火したらgetUserMediaを呼び出す
//     getUserMediaでローカルのカメラに接続
//         成功：カメラ起動＋checkImage()
//               カメラボタンを非表示にする
//         失敗：カメラ起動できなかった通知＋もとの画面に戻す

// canvas用idを取得
// ctxを設定
// checkImage:
//     動画をcanvasに描画
//     描画した情報を取得
//     jsQRに投入
//         読み取り成功：バックエンドにデータを送る
//         読み取り失敗：再試行。一定時間経過で自動的にカメラ起動を終了する？
//         ※1.ユーザーが任意にカメラを終了できる”×”ボタンが必要かも。
//           →svgでhtmlにいれて、cssでカメラ映像枠の右上あたりに配置する？
//             id指定して、押されたらカメラ起動を終了する処理をjsで書く？
//         ※2.カメラ起動時にカメラ枠内にガイド用の枠線があるといいかも。
//           →svgでhtmlにいれて、cssでabsoluteする？


// checkImage成功後の処理：
//     取得したUUIDをバックエンドに送信
//     バックエンドの処理：セッション有効を条件（login-requiredMixin）
//                         DBに該当のUUIDがあるかを検索（UUID＝user.store.uuid）?
//                             有効：成功レスポンスをフロントに返す
//                             無効：無効レスポンスをフロントに返す
//                                     クーポンは存在するが期限切れ
//                                     クーポンが存在しない：該当UUIDがDBにない、多店舗UUID
//     フロントエンドの処理：成功レスポンス：jsで使用済み表示＋続けて認証ボタンでカメラ起動
//                                           ※手入力コード用のボタンと共通になってしまう？
//                           失敗レスポンス：{% message %}とかでエラーハンドリング
//                                           ※カメラは一旦停止する？
