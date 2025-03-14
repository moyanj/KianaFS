<script setup lang="ts">
import { ElForm, ElFormItem, ElInput, ElButton, ElCard } from 'element-plus';
import { ref } from 'vue';
import { server } from '@/cfg';
import { useCookies } from 'vue3-cookies';
import { useRouter } from 'vue-router';

const cookies = useCookies().cookies;
const router = useRouter();

const form = ref({
    username: '',
    password: '',
    raw: true
});

if (cookies.get('token')) {
    router.push('/');
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
            // 设置cookie
            cookies.set('token', data.data, "7d");
            router.push('/');
        })
        .catch(error => {
            alert(error.msg);
        })
}


</script>

<template>
    <div class="co">
        <el-card class="container">
            <ElForm id="loginForm">
                <h1>KianaFS</h1>

                <ElFormItem label="用户" prop="username">
                    <ElInput v-model="form.username" placeholder="请输入用户名" />

                </ElFormItem>

                <ElFormItem label="密码" prop="password">
                    <ElInput type="password" v-model="form.password" placeholder="请输入密码" />

                </ElFormItem>

                <ElButton type="primary" class="good-button" @click="submitForm">登录</ElButton>
            </ElForm>
        </el-card>
    </div>
</template>

<style scoped>
/* 设置整个页面的居中对齐 */
.co {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    /* 添加这一行以确保容器占满整个视口高度 */
    width: 100vw;
}

.container {
    justify-content: center;
    align-items: center;
    width: 65%;
    border-radius: 10px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    text-align: center;
    margin: 0 auto;
}


.good-button {
    height: 50px;
    width: 100%;
    background: linear-gradient(135deg, #ff82af 0%, #ffdb8b 100%);
    color: white;
    font-weight: bold;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background 0.3s ease;
}

.good-button:hover {
    background: linear-gradient(135deg, #ff72a0 0%, #ffd17b 100%);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.good-button:focus {
    outline: none;
}

.good-button:active {
    transform: scale(0.98);
}
</style>
