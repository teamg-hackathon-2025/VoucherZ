// バーガーメニュー用(モバイルサイズ用)
// メニューを開く
const openBurgerButton = document.getElementById("burger-icon");
const closeBurgerButton = document.getElementById("burger-close-icon");
const menu = document.getElementById("mobile-header");

openBurgerButton.addEventListener("click", openMenu);
function openMenu() {
  openBurgerButton.style.display = "none";
  closeBurgerButton.style.display = "block";
  menu.style.display = "flex";
}

// メニューを閉じる
closeBurgerButton.addEventListener("click", closeMenu);
function closeMenu() {
  closeBurgerButton.style.display = "none";
  openBurgerButton.style.display = "block";
  menu.style.display = "none";
}

// ウィンドウサイズ変更時にメニューをリセット
window.addEventListener("resize", () => {
  if (window.innerWidth > 767) {
    menu.style.display = "";
    openBurgerButton.style.display = "";
    closeBurgerButton.style.display = "none";
  }
});
