import { useEffect, useState } from 'react';
import { adminAPI } from '../../services/api';

const AdminDashboard = ({ onLogout }) => {
    // Quản lý Tab
    const [activeTab, setActiveTab] = useState('faq'); // 'faq' hoặc 'leads'

    // State cho FAQ
    const [faqs, setFaqs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [editingId, setEditingId] = useState(null);
    const [formData, setFormData] = useState({
        category: '', keywords: '', question_intent: '', answer_text: ''
    });

    // State cho Khách hàng (Leads)
    const [leads, setLeads] = useState([]);
    const [selectedChat, setSelectedChat] = useState([]);
    const [isModalOpen, setIsModalOpen] = useState(false);

    useEffect(() => {
        fetchFAQs();
        fetchLeads();
    }, []);

    const fetchFAQs = async () => {
        try {
            const data = await adminAPI.getFAQs();
            setFaqs(data);
        } catch (error) { console.error("Lỗi tải FAQ"); } finally { setLoading(false); }
    };

    const fetchLeads = async () => {
        try {
            const data = await adminAPI.getLeads();
            setLeads(data);
        } catch (error) { console.error("Lỗi tải Leads"); }
    };

    // --- CÁC HÀM XỬ LÝ FAQ ---
    const handleDeleteFAQ = async (id) => {
        if (!window.confirm("Xóa câu hỏi này?")) return;
        await adminAPI.deleteFAQ(id);
        setFaqs(faqs.filter(faq => faq.id !== id));
    };

    const handleSubmitFAQ = async (e) => {
        e.preventDefault();
        if (editingId) {
            await adminAPI.updateFAQ(editingId, formData);
            alert("Cập nhật thành công!");
        } else {
            await adminAPI.createFAQ(formData);
            alert("Thêm mới thành công!");
        }
        setFormData({ category: '', keywords: '', question_intent: '', answer_text: '' });
        setEditingId(null);
        fetchFAQs();
    };

    // --- CÁC HÀM XỬ LÝ LEADS ---
    const openChatHistory = async (conversationId) => {
        try {
            const history = await adminAPI.getChatHistory(conversationId);
            setSelectedChat(history);
            setIsModalOpen(true);
        } catch (error) {
            alert("Không thể tải lịch sử chat");
        }
    };

    return (
        <div style={styles.container}>
            <div style={styles.header}>
                <h2>Hệ thống Quản trị VNJ</h2>
                <button style={styles.logoutBtn} onClick={onLogout}>Đăng xuất</button>
            </div>

            <div style={styles.content}>
                {/* THANH ĐIỀU HƯỚNG TABS */}
                <div style={styles.tabContainer}>
                    <button
                        style={{ ...styles.tabBtn, ...(activeTab === 'faq' ? styles.activeTab : {}) }}
                        onClick={() => setActiveTab('faq')}
                    >
                        Quản lý Tri thức (FAQ)
                    </button>
                    <button
                        style={{ ...styles.tabBtn, ...(activeTab === 'leads' ? styles.activeTab : {}) }}
                        onClick={() => setActiveTab('leads')}
                    >
                        Khách hàng Tiềm năng ({leads.length})
                    </button>
                </div>

                {/* TAB 1: QUẢN LÝ FAQ */}
                {activeTab === 'faq' && (
                    <div>
                        <form style={styles.form} onSubmit={handleSubmitFAQ}>
                            <h3>{editingId ? "Sửa câu hỏi FAQ" : "Thêm câu hỏi FAQ mới"}</h3>
                            <div style={styles.formRow}>
                                <input required placeholder="Danh mục" value={formData.category} onChange={e => setFormData({ ...formData, category: e.target.value })} style={styles.input} />
                                <input required placeholder="Mục đích" value={formData.question_intent} onChange={e => setFormData({ ...formData, question_intent: e.target.value })} style={styles.input} />
                            </div>
                            <input required placeholder="Từ khóa (giá, chi phí...)" value={formData.keywords} onChange={e => setFormData({ ...formData, keywords: e.target.value })} style={{ ...styles.input, width: '100%', marginBottom: '10px' }} />
                            <textarea required placeholder="Câu trả lời của Bot..." value={formData.answer_text} onChange={e => setFormData({ ...formData, answer_text: e.target.value })} style={styles.textarea} />
                            <div style={{ display: 'flex', gap: '10px' }}>
                                <button type="submit" style={styles.saveBtn}>Lưu dữ liệu</button>
                                {editingId && <button type="button" onClick={() => { setEditingId(null); setFormData({ category: '', keywords: '', question_intent: '', answer_text: '' }) }} style={styles.cancelBtn}>Hủy sửa</button>}
                            </div>
                        </form>

                        <table style={styles.table}>
                            <thead>
                                <tr style={styles.th}>
                                    <th style={{ padding: '10px' }}>Danh mục</th><th>Từ khóa</th><th>Câu trả lời</th><th>Hành động</th>
                                </tr>
                            </thead>
                            <tbody>
                                {faqs.map(faq => (
                                    <tr key={faq.id} style={styles.tr}>
                                        <td style={styles.td}><b>{faq.category}</b></td>
                                        <td style={styles.td}>{faq.keywords}</td>
                                        <td style={{ ...styles.td, maxWidth: '300px' }}>{faq.answer_text}</td>
                                        <td style={styles.td}>
                                            <button style={styles.editBtn} onClick={() => { setEditingId(faq.id); setFormData(faq); }}>Sửa</button>
                                            <button style={styles.deleteBtn} onClick={() => handleDeleteFAQ(faq.id)}>Xóa</button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}

                {/* TAB 2: KHÁCH HÀNG TIỀM NĂNG (LEADS) */}
                {activeTab === 'leads' && (
                    <table style={styles.table}>
                        <thead>
                            <tr style={styles.th}>
                                <th style={{ padding: '10px' }}>Mã Phiên Chat</th>
                                <th>Thông tin Liên lạc (SĐT/Email)</th>
                                <th>Hành động</th>
                            </tr>
                        </thead>
                        <tbody>
                            {leads.map(lead => (
                                <tr key={lead.id} style={styles.tr}>
                                    <td style={styles.td}>#{lead.id}</td>
                                    <td style={{ ...styles.td, color: '#28a745', fontWeight: 'bold' }}>{lead.customer_phone}</td>
                                    <td style={styles.td}>
                                        <button style={styles.viewBtn} onClick={() => openChatHistory(lead.id)}>Xem Nội dung Chat</button>
                                    </td>
                                </tr>
                            ))}
                            {leads.length === 0 && <tr><td colSpan="3" style={{ textAlign: 'center', padding: '20px' }}>Chưa có khách hàng nào để lại thông tin.</td></tr>}
                        </tbody>
                    </table>
                )}
            </div>

            {/* CỬA SỔ NỔI (MODAL) ĐỌC LỊCH SỬ CHAT */}
            {isModalOpen && (
                <div style={styles.modalOverlay}>
                    <div style={styles.modalContent}>
                        <h3 style={{ marginTop: 0, borderBottom: '1px solid #ccc', paddingBottom: '10px' }}>Lịch sử Hội thoại</h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '400px', overflowY: 'auto', padding: '10px' }}>
                            {selectedChat.map((msg, idx) => (
                                <div key={idx} style={msg.sender === 'user' ? styles.chatUser : styles.chatBot}>
                                    <b>{msg.sender === 'user' ? 'Khách hàng: ' : 'VNJ Bot: '}</b>
                                    {msg.message_text || msg.text}
                                </div>
                            ))}
                        </div>
                        <button style={styles.closeModalBtn} onClick={() => setIsModalOpen(false)}>Đóng cửa sổ</button>
                    </div>
                </div>
            )}
        </div>
    );
};

// CSS nội tuyến được bổ sung giao diện Tabs và Modal
const styles = {
    container: { fontFamily: 'Arial, sans-serif', backgroundColor: '#f4f6f9', minHeight: '100vh' },
    header: { backgroundColor: '#0056b3', color: 'white', padding: '15px 30px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
    content: { padding: '30px', maxWidth: '1200px', margin: '0 auto' },
    logoutBtn: { backgroundColor: '#dc3545', color: 'white', border: 'none', padding: '8px 15px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' },

    /* Giao diện Tabs */
    tabContainer: { display: 'flex', borderBottom: '2px solid #ccc', marginBottom: '20px' },
    tabBtn: { padding: '10px 20px', cursor: 'pointer', border: 'none', backgroundColor: 'transparent', fontSize: '16px', fontWeight: 'bold', color: '#6c757d' },
    activeTab: { borderBottom: '3px solid #0056b3', color: '#0056b3' },

    form: { backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', marginBottom: '30px' },
    formRow: { display: 'flex', gap: '15px', marginBottom: '10px' },
    input: { flex: 1, padding: '10px', border: '1px solid #ccc', borderRadius: '4px' },
    textarea: { width: '100%', padding: '10px', border: '1px solid #ccc', borderRadius: '4px', minHeight: '80px', marginBottom: '10px', resize: 'vertical' },
    saveBtn: { backgroundColor: '#28a745', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' },
    cancelBtn: { backgroundColor: '#6c757d', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '4px', cursor: 'pointer' },
    table: { width: '100%', borderCollapse: 'collapse', backgroundColor: 'white', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' },
    th: { backgroundColor: '#e9ecef', textAlign: 'left', borderBottom: '2px solid #dee2e6' },
    tr: { borderBottom: '1px solid #dee2e6' },
    td: { padding: '12px', verticalAlign: 'top' },
    editBtn: { backgroundColor: '#ffc107', border: 'none', padding: '5px 10px', marginRight: '5px', borderRadius: '3px', cursor: 'pointer' },
    deleteBtn: { backgroundColor: '#dc3545', color: 'white', border: 'none', padding: '5px 10px', borderRadius: '3px', cursor: 'pointer' },
    viewBtn: { backgroundColor: '#17a2b8', color: 'white', border: 'none', padding: '8px 12px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' },

    /* Giao diện Modal (Cửa sổ nổi) */
    modalOverlay: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 },
    modalContent: { backgroundColor: 'white', padding: '20px', borderRadius: '8px', width: '500px', display: 'flex', flexDirection: 'column' },
    chatUser: { alignSelf: 'flex-end', backgroundColor: '#cce5ff', color: '#004085', padding: '10px', borderRadius: '10px', maxWidth: '85%', border: '1px solid #b8daff' },
    chatBot: { alignSelf: 'flex-start', backgroundColor: '#f8f9fa', color: '#383d41', padding: '10px', borderRadius: '10px', maxWidth: '85%', border: '1px solid #d6d8db' },
    closeModalBtn: { marginTop: '15px', backgroundColor: '#6c757d', color: 'white', border: 'none', padding: '10px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }
};

export default AdminDashboard;