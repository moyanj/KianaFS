<script setup lang="ts">
import { ElForm, ElFormItem, ElInput, ElButton, ElCard } from 'element-plus';
import { ref } from 'vue';
import { server, changeTheme } from '@/utils';
import { useCookies } from 'vue3-cookies';
import { useRouter } from 'vue-router';
import ThemeManager from '@/components/ThemeManager.vue';

const cookies = useCookies().cookies;
const router = useRouter();

const form = ref({
    username: '',
    password: '',
    raw: true
});
const hitokoto = ref("")

if (cookies.get('token')) {
    router.push('/');
}

function getHitokoto() {
    fetch('https://v1.hitokoto.cn')
        .then(response => response.json())
        .then(data => {
            hitokoto.value = data.hitokoto + " -- " + data.from
        })
}

async function submitForm() {
    // 提交表单逻辑
    fetch(server + '/user/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(form.value)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 设置cookie
                cookies.set('token', data.data, "7d");
                router.push('/');
            } else {
                alert(data.msg);
            }
        })
        .catch(error => {
            alert(error.msg);
        })
}

getHitokoto()

</script>

<template>
    <div class="co">
        <el-card class="container">
            <ElForm id="loginForm" size="large">
                <div class="title">
                    <h1>KianaFS</h1>
                </div>
                <ElFormItem label="用户" prop="username">
                    <ElInput v-model="form.username" placeholder="请输入用户名" />

                </ElFormItem>

                <ElFormItem label="密码" prop="password">
                    <ElInput type="password" v-model="form.password" placeholder="请输入密码" />
                </ElFormItem>

                <ElButton type="primary" class="good-button" @click="submitForm">登录</ElButton>
                <br>
                <div @click="getHitokoto" class="hitokoto">
                    <p>{{ hitokoto }}</p>

                </div>
                <ThemeManager />
            </ElForm>
        </el-card>
    </div>
</template>

<style scoped>
.title {
    margin-bottom: 10vh;
    text-align: center;
}

.hitokoto {
    margin-top: 17vh;
}

/* 设置整个页面的居中对齐 */
.co {
    display: flex;
    justify-content: left;
    align-items: left;
    /* 添加这一行以确保容器占满整个视口高度 */
    width: 100vw;
    height: 100vh;
    background-size: cover;
}

.dark .co {
    background-image: url('@/assets/login_dark.jpg');
}

.light .co {
    background-image: url('@/assets/login_light.jpg');
}

.container {
    justify-content: center;
    align-items: center;
    width: 30%;
    height: calc(100% - 40px);
    border-radius: 10px;
    max-width: 380px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    text-align: center;
    margin: 20px 10px;
}


.good-button {
    margin-top: 6.5vh;

    height: 50px;
    width: 100%;
    background: linear-gradient(145deg, #ff68a0 0%, #ffcd62 100%);
    color: white;
    font-weight: bold;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background 1s ease;
}

.good-button:hover {
    background: linear-gradient(75deg, #ff72a0 0%, #ffd17b 100%);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.good-button:focus {
    outline: none;
}

.good-button:active {
    transform: scale(0.98);
}
</style>
