/* ============================================================
   App JS — Red Social de Aficiones
   Likes, comentarios, follow/unfollow, infinite-scroll del feed
   ============================================================ */

(function () {
    "use strict";

    const csrf = window.CSRF_TOKEN || "";

    function postJSON(url, data) {
        const body = new URLSearchParams(data || {});
        return fetch(url, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrf,
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body,
            credentials: "same-origin",
        }).then((r) => r.json().then((j) => ({ ok: r.ok, status: r.status, json: j })));
    }

    function getJSON(url) {
        return fetch(url, {
            headers: { "X-Requested-With": "XMLHttpRequest" },
            credentials: "same-origin",
        }).then((r) => r.json());
    }

    /* ---------- LIKES ---------- */
    document.addEventListener("click", function (e) {
        const btn = e.target.closest(".like-btn");
        if (!btn) return;

        const id = btn.dataset.id;
        postJSON(`/posts/like/${id}/`).then(({ json }) => {
            if (typeof json.likes_count === "undefined") return;
            const counter = document.getElementById(`likes-count-${id}`);
            if (counter) counter.innerText = json.likes_count;
            btn.classList.toggle("is-liked", !!json.liked);
            const icon = btn.querySelector(".like-icon");
            if (icon) icon.textContent = json.liked ? "❤️" : "🤍";
        });
    });

    /* ---------- COMENTARIOS: toggle ---------- */
    document.addEventListener("click", function (e) {
        const tog = e.target.closest(".comment-toggle");
        if (!tog) return;
        const id = tog.dataset.id;
        const section = document.getElementById(`comments-section-${id}`);
        if (section) section.hidden = !section.hidden;
    });

    /* ---------- COMENTARIOS: submit ---------- */
    document.addEventListener("submit", function (e) {
        const form = e.target.closest(".comment-form");
        if (!form) return;
        e.preventDefault();

        const postId = form.dataset.postId;
        const input = form.querySelector('input[name="content"], textarea[name="content"]');
        const value = (input && input.value || "").trim();
        if (!value) return;

        postJSON(`/posts/comment/${postId}/`, { content: value }).then(({ ok, json }) => {
            if (!ok || !json.ok) return;

            const list = document.getElementById(`comments-list-${postId}`);
            if (list) {
                const li = document.createElement("li");
                li.className = "comment-item";
                li.innerHTML = `<strong></strong> <span class="comment-content"></span> <small class="comment-date"></small>`;
                li.querySelector("strong").textContent = json.comment.author;
                li.querySelector(".comment-content").textContent = json.comment.content;
                li.querySelector(".comment-date").textContent = json.comment.created_at;
                list.appendChild(li);
            }

            const counter = document.getElementById(`comments-count-${postId}`);
            if (counter) counter.textContent = json.comments_count;

            input.value = "";
        });
    });

    /* ---------- FOLLOW / UNFOLLOW ---------- */
    document.addEventListener("click", function (e) {
        const btn = e.target.closest(".follow-btn");
        if (!btn) return;

        const userId = btn.dataset.userId;
        const isFollowing = btn.dataset.following === "1";
        const url = isFollowing
            ? `/posts/unfollow/${userId}/`
            : `/posts/follow/${userId}/`;

        btn.disabled = true;

        postJSON(url).then(({ ok, json }) => {
            btn.disabled = false;
            if (!ok || !json.ok) return;
            btn.dataset.following = json.following ? "1" : "0";
            btn.classList.toggle("is-following", json.following);
            btn.textContent = json.following ? "Siguiendo" : "Seguir";

            const counter = document.getElementById(`followers-count-${userId}`);
            if (counter && typeof json.followers_count !== "undefined") {
                counter.textContent = json.followers_count;
            }
        });
    });

    /* ---------- INFINITE SCROLL DEL FEED ---------- */
    const loader = document.getElementById("feed-loader");
    if (loader) {
        const list = document.getElementById("post-list");
        const btn = document.getElementById("load-more-btn");
        let nextPage = parseInt(loader.dataset.next, 10);
        const url = loader.dataset.url;
        let loading = false;

        function loadMore() {
            if (loading || !nextPage) return;
            loading = true;
            btn.textContent = "Cargando...";

            getJSON(`${url}?page=${nextPage}`)
                .then((data) => {
                    if (data.html) list.insertAdjacentHTML("beforeend", data.html);
                    if (data.has_next) {
                        nextPage = data.next_page;
                        btn.textContent = "Cargar más";
                    } else {
                        loader.remove();
                    }
                })
                .catch(() => {
                    btn.textContent = "Reintentar";
                })
                .finally(() => {
                    loading = false;
                });
        }

        btn.addEventListener("click", loadMore);

        // Auto-cargar al hacer scroll cerca del final
        const io = new IntersectionObserver(
            (entries) => {
                if (entries.some((en) => en.isIntersecting)) loadMore();
            },
            { rootMargin: "300px" }
        );
        io.observe(loader);
    }
})();
