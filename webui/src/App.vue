<script setup lang="ts">
import { RouterView, useRouter } from 'vue-router';
import { ElMenu, ElMenuItem } from 'element-plus';
import { ref, watch, onMounted, onUnmounted } from "vue";
import { changeTheme } from "./utils";
import { useCookies } from 'vue3-cookies';
import TablerDashboard from '~icons/tabler/dashboard';
import TablerFile from '~icons/tabler/file';
import TablerDatabase from '~icons/tabler/database';
import TablerUser from '~icons/tabler/user';
import TablerSettings from '~icons/tabler/settings'

// 定义 active 引用的类型
const active = ref("");

const { cookies } = useCookies();

// 使用 useRouter 钩子
const router = useRouter();
// 监听路由变化以更新 active 引用
watch(
    () => router.currentRoute.value.path,
    (newPath) => {
        const baseUrl = import.meta.env.BASE_URL;
        active.value = newPath.startsWith(baseUrl) ? newPath.slice(baseUrl.length) : newPath;
        console.log(active.value);
    },
    { immediate: true } // 立即执行一次以设置初始值
);

const updateTheme = () => {
    if (cookies.get("theme") === 'auto') {
        const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        changeTheme(isDark ? 'dark' : 'light');
    } else {
        changeTheme(cookies.get("theme"));
    }
};

onMounted(() => {
    updateTheme();
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', updateTheme);
    window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', updateTheme);
});

onUnmounted(() => {
    window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', updateTheme);
    window.matchMedia('(prefers-color-scheme: light)').removeEventListener('change', updateTheme);
});
</script>

<template>
    <el-menu class="header-menu" :class="{ 'hidden': active === '/login' }" :route="true" :default-active="active">
        <el-menu-item class="header-menu-title">
            <span>KianaFS</span>
        </el-menu-item>
        <el-menu-item index="/" @click="router.push('/')">
            <TablerDashboard />&nbsp;概览
        </el-menu-item>
        <el-menu-item index="/storagers" @click="router.push('/storagers')">
            <TablerDatabase />&nbsp;存储管理
        </el-menu-item>
        <el-menu-item index="/files" @click="router.push('/files')">
            <TablerFile />&nbsp;文件管理
        </el-menu-item>
        <el-menu-item index="/users" @click="router.push('/users')">
            <TablerUser />&nbsp;用户管理
        </el-menu-item>
        <el-menu-item index="/settings" @click="router.push('/settings')">
            <TablerSettings />&nbsp;设置
        </el-menu-item>

    </el-menu>

    <RouterView />
</template>

<style scoped>
.header-menu {
    width: 12.5vw;
    height: 100vh;
    margin-right: 1vw;
}

.header-menu-title {
    span {
        font-size: 2vw;
        text-align: center;
    }
}

.hidden {
    display: none;
}

.el-card {
    width: 100%;
    height: 100%;
    --el-card-padding: 0;
}
</style>

<style>
#app {
    display: flex;
}
</style>