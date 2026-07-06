import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

apiClient.interceptors.response.use(
    (response) => {
        // Nếu gọi API thành công, cứ để dữ liệu đi qua bình thường
        return response;
    },
    (error) => {
        // Nếu Backend báo lỗi 401 (Token hết hạn hoặc sai)
        if (error.response && error.response.status === 401) {
            alert("Phiên đăng nhập đã hết hạn để đảm bảo an toàn. Vui lòng đăng nhập lại!");
            localStorage.removeItem('vnj_admin_token'); // Xóa chìa khóa hỏng
            window.location.href = '/admin'; // Đá văng ra ngoài trang Login
        }

        if (error.response && error.response.status === 429) {
            alert("Bạn đang gửi tin nhắn quá nhanh! Vui lòng chờ vài giây rồi thử lại nhé.");
        }

        return Promise.reject(error);
    }
);

const getAuthHeader = () => {
    const token = localStorage.getItem('vnj_admin_token');
    return { Authorization: `Bearer ${token}` };
};

// ==========================================
// 1. CÁC API DÀNH CHO KHÁCH HÀNG (CHATBOT)
// ==========================================
export const chatAPI = {
    startChat: async (customerName = "Khách hàng ẩn danh", customerPhone = "") => {
        // Thêm /chat/ vào đây
        const response = await apiClient.post('/chat/start', {
            customer_name: customerName,
            customer_phone: customerPhone
        });
        return response.data;
    },

    sendMessage: async (sessionId, messageText) => {
        // Thêm /chat/ vào đây
        const response = await apiClient.post('/chat/message', {
            session_id: sessionId,
            message_text: messageText
        });
        return response.data;
    }
};

// ==========================================
// 2. CÁC API DÀNH CHO ADMIN (QUẢN TRỊ)
// ==========================================
export const adminAPI = {
    login: async (username, password) => {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        // Gọi thẳng vào /auth/login
        const response = await apiClient.post('/auth/login', formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        });
        return response.data;
    },

    getFAQs: async () => {
        // Gọi thẳng vào /faq/
        const response = await apiClient.get('/faq/', { headers: getAuthHeader() });
        return response.data;
    },

    createFAQ: async (faqData) => {
        const response = await apiClient.post('/faq/', faqData, { headers: getAuthHeader() });
        return response.data;
    },

    updateFAQ: async (faqId, faqData) => {
        const response = await apiClient.put(`/faq/${faqId}`, faqData, { headers: getAuthHeader() });
        return response.data;
    },

    deleteFAQ: async (faqId) => {
        const response = await apiClient.delete(`/faq/${faqId}`, { headers: getAuthHeader() });
        return response.data;
    },

    getLeads: async () => {
        const response = await apiClient.get('/chat/leads', { headers: getAuthHeader() });
        return response.data;
    },

    getChatHistory: async (conversationId) => {
        const response = await apiClient.get(`/chat/history/${conversationId}`, { headers: getAuthHeader() });
        return response.data;
    }
};

