const startBtn = document.getElementById('start-qr');
const startGuide = document.getElementById('start-guide');
const frame = document.getElementById('frame');
const closeBtn = document.getElementById('close-qr');
const video  = document.getElementById('video');
const qrErrorArea = document.getElementById('qr-error-area');


// カメラ起動
let stream;
async function startCamera() {
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
    
    qr_check = false;
    scanning = true;
    checkImage();
    startBtn.style.display = 'none';
    startGuide.style.display = 'none';
    closeBtn.style.display = 'block';
    frame.style.display = 'block';
}

startBtn.addEventListener('click', startCamera);

// QRコードをスキャン
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d', { willReadFrequently: true })

let qr_check = false; // true:QRコード読み取り成功 false:読み取り失敗or未チェック
let scanning = true; // true:checkImage稼働許可 false:checkImage停止
const checkImage = async () => {
    if (!scanning) return;
    
    // 取得している動画をCanvasに描画
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Canvasからデータを取得
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    
    // jsQRに渡す
    const code = jsQR(imageData.data, canvas.width, canvas.height);
    
    // QRコードの読み取りに成功したら値を出力
    // 失敗したら再度実行
    if (!qr_check && code) {
        qr_check = true;
        scanning = false;

        // QRコードデータを取得
        const qrData = code.data

        // Djangoへ送信する
        try {
            const qrResponse = await fetch(`/coupon/api/verify/uuid/${qrData}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({})
            });
            const qrResult = await qrResponse.json();

            if (qrResponse.ok && qrResult.success) {
                qrErrorArea.style.display = "none";
                titleArea.style.display = "none";
                cameraArea.style.display = "none";
                manualArea.style.display = "none";
                resultArea.style.display = "flex";
                resultArea.innerHTML = `
                    <h2 class="result-title">☑使用済み</h2>
                    <p class="result-text">以下のクーポンを使用済みにしました。</p>
                    <p class="result-label">＜商品名＞</p>
                    <p class="result-item">${qrResult.target_product}</p>
                    <p class="result-label">＜割引内容＞</p>
                    <p class="result-item">${qrResult.discount}</p>
                    <div class="button-container">
                        <button type="button" id="next-verify">次を認証</button>
                        <button type="button" id="end-verify">終了する</button>
                    </div>
                `;

                // カメラ停止し認証画面に戻る
                document.getElementById("end-verify").addEventListener("click", () => {
                    resetVerificationUI();
                });

                // カメラ起動し認証を続ける
                document.getElementById("next-verify").addEventListener("click", () => {
                    resetVerificationUI();
                    startCamera();
                });
            } else {
                qrErrorArea.style.display = "block";
                manualErrorArea.style.display = "none";
                qrErrorArea.innerText = qrResult.error;
            }
        } catch(error) {
            console.error('送信できない', error);
            qrErrorArea.style.display = "block";
            qrErrorArea.innerText = "通信エラーが発生しました";
        }
        // カメラ停止、画面リセット
        stopCameraAndResetUI();
    } else {
        qr_check = false;
        setTimeout(() => { checkImage() }, 500);
    }
};

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


// クーポンコード認証
const resultArea = document.getElementById('result-area'); // 成功時の画面表示
const manualErrorArea = document.getElementById('manual-error-area'); // エラー時の画面表示
const titleArea = document.getElementById('title-area'); // 成功時に非表示
const cameraArea = document.getElementById('camera-area'); // 成功時に非表示
const manualArea = document.getElementById('manual-area'); // 成功時に非表示

const manualVerify = document.getElementById('manual-verify');
manualVerify.addEventListener('click', async () => {
    scanning = false;
    qr_check = false;
    stopCameraAndResetUI();
    
    const manualCode = document.getElementById('verification-code').value.trim();
    if (!manualCode) {
        manualErrorArea.innerText = "コードを入力してください";
        return;
    }
    
    // Djangoへ送信
    try {
        const manualResponse = await fetch(`/coupon/api/verify/manual/${manualCode}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({})
        })
        const manualResult = await manualResponse.json();

        if (manualResponse.ok && manualResult.success) {
            manualErrorArea.style.display = "none";
            titleArea.style.display = "none";
            cameraArea.style.display = "none";
            manualArea.style.display = "none";
            resultArea.style.display = "flex";
            resultArea.innerHTML = `
                    <h2 class="result-title">☑使用済み</h2>
                    <p class="result-text">以下のクーポンを使用済みにしました。</p>
                    <p class="result-label">＜商品名＞</p>
                    <p class="result-item">${manualResult.target_product}</p>
                    <p class="result-label">＜割引内容＞</p>
                    <p class="result-item">${manualResult.discount}</p>
                    <div class="button-container">
                        <button type="button" id="next-verify">次を認証</button>
                    </div>
                `;

            // もとの画面に戻る
            document.getElementById("next-verify").addEventListener("click", () => {
                resetVerificationUI();
            });
        } else {
            manualErrorArea.style.display = "block";
            qrErrorArea.style.display = "none";
            manualErrorArea.innerText = manualResult.error;
        }
    } catch(error) {
        console.error('送信できない', error);
        manualErrorArea.style.display = "block";
        manualErrorArea.innerText = "通信エラーが発生しました";
    }
        // カメラ停止、画面リセット
        stopCameraAndResetUI();
})

// カメラを手動で停止
closeBtn.addEventListener('click', () => {
    stopCameraAndResetUI();
    qr_check = false;
    scanning = false;
});

//  カメラを停止してUIをデフォルト状態に戻す関数
function stopCameraAndResetUI() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
    video.srcObject = null;
    startBtn.style.display = 'block';
    startGuide.style.display = 'block';
    closeBtn.style.display = 'none';
    frame.style.display = 'none';
}

// 認証後のUIをリセットする関数
function resetVerificationUI() {
    titleArea.style.display = "block";
    cameraArea.style.display = "block";
    manualArea.style.display = "block";
    resultArea.innerHTML = "";
    resultArea.style.display = "none";
}




