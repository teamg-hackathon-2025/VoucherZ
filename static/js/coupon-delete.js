// ホーム画面のクーポン一覧を削除するモーダルの制御

export const initDeleteCouponListModal = () => {
  const deleteCouponListModal = document.getElementById("deleteCouponListModal");
  const openButtons = document.querySelectorAll(".delete-button");
  const closeButton = document.getElementById("closeDeleteCouponListModal");
  const form = document.getElementById("deleteCouponListForm");

  openButtons.forEach((button) => {
    button.addEventListener("click", (e) => {
      e.preventDefault();
      const url = button.dataset.deleteUrl;
      if (url && form) form.action = url;
      deleteCouponListModal.style.display = "flex";
    });
  });
  if (closeButton) {
    closeButton.addEventListener("click", () => {
      deleteCouponListModal.style.display = "none";
    });
  }
  window.addEventListener("click", (e) => {
    if (e.target === deleteCouponListModal) {
      deleteCouponListModal.style.display = "none";
    }
  });
};

document.addEventListener("DOMContentLoaded", () => {
  initDeleteCouponListModal();
});