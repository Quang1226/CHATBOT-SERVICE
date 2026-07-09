import { useState } from 'react';
import { adminAPI } from '../../services/api';

const AdminLogin = ({ onLoginSuccess }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            // Gọi API sang Backend để kiểm tra
            const data = await adminAPI.login(username, password);

            // Nếu đúng, lưu Chìa khóa (Token) vào két sắt của trình duyệt
            localStorage.setItem('vnj_admin_token', data.access_token);

            // Báo cáo đăng nhập thành công
            onLoginSuccess();
        } catch (err) {
            // In thẳng lỗi ra bảng Console (F12) để chúng ta xem
            console.error("Lỗi chi tiết:", err.response || err);

            // Phân loại lỗi để hiển thị ra màn hình
            if (err.response && err.response.status === 401) {
                setError('Sai tài khoản hoặc mật khẩu thật rồi!');
            } else {
                // Nếu bị lỗi 422 hoặc lỗi khác, nó sẽ in thẳng ra đây
                setError('Lỗi hệ thống: ' + (err.response?.data?.detail || err.message));
            }
        }
    };

    return (
        <div style={styles.container}>
            <form style={styles.form} onSubmit={handleLogin}>
                <h2 style={{ textAlign: 'center', color: '#0056b3' }}>Quản trị VNJ Chatbot</h2>
                {error && <p style={{ color: 'red', fontSize: '14px', textAlign: 'center' }}>{error}</p>}

                <input
                    style={styles.input}
                    type="text"
                    placeholder="Tên đăng nhập"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />
                <input
                    style={styles.input}
                    type="password"
                    placeholder="Mật khẩu"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                <button style={styles.button} type="submit">Đăng nhập</button>
            </form>
        </div>
    );
};

// CSS viết trực tiếp cho nhanh gọn
const styles = {
    container: { display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', backgroundColor: '#f0f2f5' },
    form: { backgroundColor: 'white', padding: '30px', borderRadius: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', width: '300px', display: 'flex', flexDirection: 'column', gap: '15px' },
    input: { padding: '10px', borderRadius: '4px', border: '1px solid #ccc', fontSize: '16px' },
    button: { padding: '10px', borderRadius: '4px', border: 'none', backgroundColor: '#0056b3', color: 'white', fontSize: '16px', cursor: 'pointer', fontWeight: 'bold' }
};

export default AdminLogin;