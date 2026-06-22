import { useEffect, useState } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import ChatWidget from './components/ChatWidget';
import AdminDashboard from './pages/Admin/AdminDashboard';
import AdminLogin from './pages/Admin/AdminLogin';

// Trang chủ giả lập của VNJ (Chứa Chatbot)
const HomePage = () => (
    <div className="app-container">
        <h1 style={{ padding: '20px', fontFamily: 'sans-serif' }}>Website Công ty TNHH Công nghệ VNJ</h1>
        <ChatWidget />
    </div>
);

// Khu vực quản trị Admin
const AdminArea = () => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    // Kiểm tra xem trình duyệt có giữ Token cũ không
    useEffect(() => {
        const token = localStorage.getItem('vnj_admin_token');
        if (token) setIsAuthenticated(true);
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('vnj_admin_token');
        setIsAuthenticated(false);
    };

    if (!isAuthenticated) {
        return <AdminLogin onLoginSuccess={() => setIsAuthenticated(true)} />;
    }

    // Gọi bảng điều khiển ra và truyền hàm Logout vào
    return <AdminDashboard onLogout={handleLogout} />;
};

function App() {
    return (
        <BrowserRouter>
            <Routes>
                {/* Đường dẫn gốc: Trang chủ dành cho Khách hàng */}
                <Route path="/" element={<HomePage />} />

                {/* Đường dẫn ẩn: Dành cho Admin */}
                <Route path="/admin" element={<AdminArea />} />

                {/* Gõ sai đường dẫn thì tự động chuyển về Trang chủ */}
                <Route path="*" element={<Navigate to="/" />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;