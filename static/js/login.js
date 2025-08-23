// 目のアイコンのid
const togglePassword = document.querySelector("#togglePassword");
// フィールドのid
const passwordInput = document.querySelector("#password");

togglePassword.addEventListener("click", () => {
    const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
    passwordInput.setAttribute("type", type);

    // アイコンを切り替える
    if (type === "password") {
        togglePassword.src = "/static/img/eye-slash.svg";
        togglePassword.alt = "パスワード非表示";
    } else {
        togglePassword.src = "/static/img/eye.svg";
        togglePassword.alt = "パスワード表示";
    }
});


