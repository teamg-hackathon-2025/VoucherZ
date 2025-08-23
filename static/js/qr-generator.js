document.addEventListener("DOMContentLoaded", () => {
  const qrCodeDiv = document.getElementById("qrCode");
  const mode = qrCodeDiv.dataset.mode;
  const size = +qrCodeDiv.dataset.size || 200;
  const text = mode === "url" ? qrCodeDiv.dataset.url : qrCodeDiv.dataset.uuid;

  new QRCode(qrCodeDiv, {
    text: text,
    width: size,
    height: size
  });
});