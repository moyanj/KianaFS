<script setup lang="ts">
import { getTheme, changeTheme } from "../utils";
import { ref } from "vue";
import { ElButton } from "element-plus";
import TablerSun from '~icons/tabler/sun';
import TablerMoon from '~icons/tabler/moon';

const theme = ref(getTheme());

function change() {
    if (theme.value === "dark") {
        theme.value = "light";
    } else {
        theme.value = "dark";
    }
    changeTheme(theme.value);
}
</script>

<template>
    <el-button @click="change()">
        <template v-if="theme === 'dark'">
            <TablerSun />
        </template>
        <template v-else>
            <TablerMoon />
        </template>
    </el-button>
</template>

<style scoped></style>