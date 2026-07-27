/*! coi-serviceworker v0.1.7 | MIT License | https://github.com/gzuidhof/coi-serviceworker */
if (typeof window === 'undefined') {
    self.addEventListener("install", () => self.skipWaiting());
    self.addEventListener("activate", (event) => event.waitUntil(self.clients.claim()));

    self.addEventListener("fetch", (event) => {
        const r = event.request;
        if (r.cache === "only-if-cached" && r.mode !== "same-origin") {
            return;
        }

        let request = r;
        // Upgrade cross-origin no-cors requests to cors so they don't return opaque (status 0) responses
        // which are blocked by COEP require-corp. CDNs like cdnjs and jsdelivr support CORS.
        const isCrossOrigin = new URL(r.url).origin !== self.location.origin;
        if (isCrossOrigin && r.mode === "no-cors") {
            // We only pass mode and credentials. If we pass the original headers, we might pass
            // conditional headers (If-None-Match) from a no-cors cache state, forcing a 304 response
            // that the browser fails to resolve with the body. Letting the browser handle the fetch
            // normally under CORS mode fixes this.
            request = new Request(r.url, {
                mode: "cors",
                credentials: "omit"
            });
        }

        event.respondWith(
            fetch(request)
                .then((response) => {
                    if (response.status === 0) {
                        return response;
                    }

                    const newHeaders = new Headers(response.headers);
                    newHeaders.set("Cross-Origin-Embedder-Policy", "require-corp");
                    newHeaders.set("Cross-Origin-Opener-Policy", "same-origin");
                    // Required: under COEP require-corp, all cross-origin resources must have CORP.
                    // CDNs (Monaco, Pyodide, RequireJS, Google Fonts) don't send this header,
                    // so the service worker adds it to every response to satisfy COEP.
                    newHeaders.set("Cross-Origin-Resource-Policy", "cross-origin");

                    // Response with status 101, 103, 204, 205, or 304, or a HEAD request, cannot have a body
                    const body = (request.method === "HEAD" || [101, 103, 204, 205, 304].includes(response.status))
                        ? null
                        : response.body;

                    return new Response(body, {
                        status: response.status,
                        statusText: response.statusText,
                        headers: newHeaders,
                    });
                })
                .catch((e) => {
                    console.error("COOP/COEP fetch interception error:", e);
                })
        );
    });
} else {
    (() => {
        // If already isolated, clean up reload flag and do nothing
        if (window.crossOriginIsolated) {
            window.sessionStorage.removeItem("coiReloadedBySelf");
            return;
        }

        // Service worker cannot be run over file:// protocol
        if (window.location.protocol === "file:") {
            console.warn("COOP/COEP Service Worker cannot run over file:// protocol. Open with localhost or deploy to a web server.");
            return;
        }

        if (navigator.serviceWorker) {
            // Find script source path
            const script = window.document.currentScript;
            const scriptSrc = script ? script.src : "coi-serviceworker.js";

            navigator.serviceWorker.register(scriptSrc).then((registration) => {
                console.log("COOP/COEP Service Worker registered with scope: ", registration.scope);

                registration.addEventListener("updatefound", () => {
                    console.log("Signaling reload due to Service Worker update...");
                    window.location.reload();
                });

                // Check if page needs reload to activate worker control
                if (!navigator.serviceWorker.controller) {
                    if (!window.sessionStorage.getItem("coiReloadedBySelf")) {
                        window.sessionStorage.setItem("coiReloadedBySelf", "true");
                        console.log("First registration: Reloading page to activate service worker.");
                        window.location.reload();
                    } else {
                        console.warn("Service worker registered but not controlling the page, and reload flag is already set. Preventing reload loop.");
                    }
                }
            }).catch((err) => {
                console.error("COOP/COEP Service Worker registration failed: ", err);
            });
        }
    })();
}
