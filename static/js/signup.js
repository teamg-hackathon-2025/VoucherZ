const togglePassword = document.getElementById("togglePassword");
const passwordInput = document.getElementById("password");

const togglePasswordConfirm = document.getElementById("togglePasswordConfirm");
const passwordConfirmInput = document.getElementById("password_confirm");

togglePassword.addEventListener("click", () => {
    const type = passwordInput.type === "password" ? "text" : "password";
    passwordInput.type = type;

    // アイコンを切り替える
    if (type === "password") {
        togglePassword.src = "/static/img/eye-slash.svg";
        togglePassword.alt = "パスワード非表示";
    } else {
        togglePassword.src = "/static/img/eye.svg";
        togglePassword.alt = "パスワード表示";
    }
});

togglePasswordConfirm.addEventListener("click", () => {
    const type = passwordConfirmInput.type === "password" ? "text" : "password";
    passwordConfirmInput.type = type;

    // アイコンを切り替える
    if (type === "password") {
        togglePasswordConfirm.src = "/static/img/eye-slash.svg";
        togglePasswordConfirm.alt = "パスワード非表示";
    } else {
        togglePasswordConfirm.src = "/static/img/eye.svg";
        togglePasswordConfirm.alt = "パスワード表示";
    }
});
