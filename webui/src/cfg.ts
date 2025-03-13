export var server: string;
if (import.meta.env.PROD) {
    server = "/api"
} else {
    server = "http://localhost:8000/api"
}

