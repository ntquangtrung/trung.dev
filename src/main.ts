import "@/assets/main.css";

import App from "@/App.vue";
import router from "@/router";
import { i18nManager } from "@/services/i18n";
import { createApp } from "vue";

const app = createApp(App);

app.use(router);
app.use(i18nManager.init());

app.mount("#root");
