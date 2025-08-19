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
