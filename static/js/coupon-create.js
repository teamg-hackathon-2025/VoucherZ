// 発行数の上限入力欄での入力制限
// 1. 入力前：数字以外をブロック
document.getElementById("maxIssuance").addEventListener("beforeinput", function(e) {
  if (e.data && /[^0-9０-９]/.test(e.data)) {
    e.preventDefault();
  }
});
// 2. 入力後：全角数字を半角へ変換、先頭が0の場合削除
document.getElementById("maxIssuance").addEventListener("input", function() {
  this.value = this.value.replace(/[０-９]/g, s =>
    String.fromCharCode(s.charCodeAt(0) - 0xFEE0)
  );
  if (this.value.startsWith("0")) {
    this.value = this.value.replace(/^0+/, '');
  }
});

// 有効期限：input dateの今日以前の選択不可設定
const today = new Date();
function dateFormat(date){
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}
const data = dateFormat(today);
const field = document.getElementById("expirationDate");
field.min = data;

// フォーム送信時のバリデーション
// 各入力欄と隣接するチェックボックスのペアについて：
// 1) 入力欄が空かつチェックも未選択 → エラー
// 2) 入力欄が入力済みかつチェックも選択 → エラー
// どちらか一方のみ入力されている場合のみ送信を許可する
document.getElementById("form").addEventListener("submit", function(e) {
  function validatePair(inputId, checkboxId, labelName) {
    const input = document.getElementById(inputId);
    const checkbox = document.getElementById(checkboxId);
    const value = input.value.trim();

    if (value === "" && !checkbox.checked) {
      alert(`${labelName}を入力するか、チェックを入れてください。`);
      return false;
    }

    if (value !== "" && checkbox.checked) {
      alert(`${labelName}の入力とチェックは同時にできません。`);
      return false;
    }

    return true;
  }

  if (
    !validatePair("maxIssuance", "noMaxIssuance", "発行数の上限") ||
    !validatePair("expirationDate", "noExpirationDate", "有効期限")
  ) {
    e.preventDefault();
  }
});
