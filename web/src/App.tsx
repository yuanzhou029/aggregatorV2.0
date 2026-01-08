import React from 'react';
import { Layout, Menu, Button, Space } from 'antd';
import { 
  AppstoreOutlined, 
  SettingOutlined, 
  DashboardOutlined,
  ToolOutlined,
  LogoutOutlined
} from '@ant-design/icons';
import { Routes, Route, useNavigate } from 'react-router-dom';
import PluginManager from './components/PluginManager';
import ConfigManager from './components/ConfigManager';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import SystemConfig from './components/SystemConfig';
import { useAuth } from './contexts/AuthContext';

const { Header, Content, Sider } = Layout;

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  const navigate = useNavigate();
  
  if (loading) {
    return <div>加载中...</div>;
  }
  
  if (!isAuthenticated) {
    navigate('/login');
    return null;
  }
  
  return <>{children}</>;
};

const Sidebar: React.FC = () => {
  const [selectedKey, setSelectedKey] = React.useState('dashboard');
  const navigate = useNavigate();
  const { logout } = useAuth();
  
  const handleMenuClick = (key: string) => {
    setSelectedKey(key);
    navigate(`/${key}`);
  };
  
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  return (
    <Sider width={200} className="site-layout-background">
      <div style={{ padding: '16px', textAlign: 'center', borderBottom: '1px solid #ddd' }}>
        <h3 style={{ color: '#fff', margin: 0 }}>菜单</h3>
      </div>
      <Menu
        mode="inline"
        selectedKeys={[selectedKey]}
        style={{ height: 'calc(100% - 70px)', borderRight: 0 }}
        items={[
          {
            key: 'dashboard',
            icon: <DashboardOutlined />, 
            label: '仪表板',
            onClick: () => handleMenuClick('dashboard')
          },
          {
            key: 'plugins',
            icon: <AppstoreOutlined />, 
            label: '插件管理',
            onClick: () => handleMenuClick('plugins')
          },
          {
            key: 'config',
            icon: <SettingOutlined />, 
            label: '配置管理',
            onClick: () => handleMenuClick('config')
          },
          {
            key: 'system',
            icon: <SettingOutlined />, 
            label: '系统配置',
            onClick: () => handleMenuClick('system')
          }
        ]}
      />
      <div style={{ position: 'absolute', bottom: 0, width: '100%', padding: '16px', borderTop: '1px solid #ddd' }}>
        <Space>
          <Button type="primary" danger icon={<LogoutOutlined />} onClick={handleLogout}>
            退出登录
          </Button>
        </Space>
      </div>
    </Sider>
  );
};

const MainContent: React.FC = () => {
  return (
    <Layout style={{ padding: '24px' }}>
      <Content className="site-layout-background" style={{ padding: 24, margin: 0, minHeight: 280 }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/plugins" element={<PluginManager />} />
          <Route path="/config" element={<ConfigManager />} />
          <Route path="/system" element={<SystemConfig />} />
        </Routes>
      </Content>
    </Layout>
  );
};

const App: React.FC = () => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>加载中...</div>;
  }
  
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header className="header" style={{ color: '#fff', fontSize: '18px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>Aggregator 管理系统</div>
        {isAuthenticated && (
          <div style={{ color: '#fff', fontSize: '14px' }}>
            欢迎, admin
          </div>
        )}
      </Header>
      <Layout>
        {isAuthenticated ? (
          <>
            <Sidebar />
            <MainContent />
          </>
        ) : (
          <Content style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="*" element={<Login />} />
            </Routes>
          </Content>
        )}
      </Layout>
    </Layout>
  );
};

export default App;