import { useCookies } from "vue3-cookies";

const { cookies } = useCookies();

export var server: string;
if (import.meta.env.PROD) {
    server = "/api"
} else {
    server = "http://localhost:8000/api"
}

export function changeTheme(theme?: string): void {

    const root = document.documentElement;
    if (theme === undefined || theme === 'auto') {
        theme = root.getAttribute('class') === 'dark' ? 'light' : 'dark';
    }
    console.log("Changing theme to " + theme);
    cookies.set('theme', theme);
    root.setAttribute('class', theme);
}

export function getTheme(): string | null {
    return document.documentElement.getAttribute('class');
}

