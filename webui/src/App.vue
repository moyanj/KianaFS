<script setup lang="ts">
import { RouterLink, RouterView, useRouter } from 'vue-router';
import { ElMenu, ElMenuItem } from 'element-plus';
import { ref, watch } from "vue";

// 定义 active 引用的类型
const active = ref<string>("");

// 使用 useRouter 钩子
const router = useRouter();
console.log(import.meta.env.BASE_URL)
// 监听路由变化以更新 active 引用
watch(
    () => router.currentRoute.value.path,
    (newPath) => {
        active.value = "/" + newPath.split("/")[1];
        console.log(import.meta.env.BASE_URL)
    },
    { immediate: true } // 立即执行一次以设置初始值
);
</script>

<template>
    <el-menu class="header-menu">
        <el-menu-item class="header-menu-title">
            <span>KianaFS</span>
        </el-menu-item>
        <el-menu-item index="/">
            <router-link to="/">Home</router-link>
        </el-menu-item>
        <el-menu-item index="/about">
            <router-link to="/about">About</router-link>
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
</style>

<style>
#app {
    display: flex;
}
</style>