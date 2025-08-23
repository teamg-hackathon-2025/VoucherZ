from django.urls import resolve, Resolver404


class ClearFlowSessionOnLeaveMiddleware:
    """
    - HTMLページ遷移のGETだけを見る（XHR/静的ファイルを除外）
    - 現在のURLがフローのallowリスト外なら、該当セッションキーをpopする
    - 複数フローに対応
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # ---- 判定: ナビゲーションっぽいリクエストだけを対象 ----
        is_get = request.method == "GET"
        accept = request.headers.get("Accept", "")
        is_page_nav = "text/html" in accept  # ページ遷移(HTML)に限定
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
        path = request.path_info or "/"

        if is_get and is_page_nav and not is_ajax:
            # 静的配信などは対象外
            for cfg in getattr(request, "FLOW_GUARDS", None) or []:
                pass  # (型ヒント対策用ダミー)

            try:
                match = resolve(path)
                ns = ":".join(match.namespaces) if match.namespaces else ""
                name = match.url_name
            except Resolver404:
                # ルーティング外 = フロー外とみなす（例えば404ページへ）
                ns, name = None, None

            from django.conf import settings
            flow_guards = getattr(settings, "FLOW_GUARDS", [])

            for flow in flow_guards:
                key = flow["session_key"]
                if key not in request.session:
                    continue  # このフローの途中ではない

                # 静的プレフィックスは常に無視
                if any(path.startswith(pref) for pref in flow.get("ignore_prefixes", ())):
                    continue

                # 現在地がフロー内か？
                allow = flow.get("allow", [])
                in_flow = any(
                    (ns == allowed_ns and name == allowed_name)
                    for (allowed_ns, allowed_name) in allow
                )

                if not in_flow:
                    # フロー外に出たのでセッションを掃除
                    request.session.pop(key, None)

        return self.get_response(request)