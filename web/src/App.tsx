import React from 'react';
import { Layout, Menu, Button, Dropdown, Space, Drawer, Avatar } from 'antd';
import { 
  SettingOutlined, 
  ApiOutlined, 
  ProfileOutlined,
  ToolOutlined,
  UserOutlined,
  LogoutOutlined,
  MenuOutlined,
  HomeOutlined,
  BarChartOutlined,
  CloudSyncOutlined,
  AppstoreOutlined
} from '@ant-design/icons';
import { Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import PluginManager from './components/PluginManager';
import ConfigManager from './components/ConfigManager';
import StatusMonitor from './components/StatusMonitor';

const { Header, Content } = Layout;

const AppContent: React.FC = () => {
  const { isAuthenticated, user, loading, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  // 处理退出登录
  const handleLogout = () => {
    logout();
    navigate('/'); // 退出后跳转到首页
  };

  // 用户菜单
  const userMenu = (
    <Menu
      onClick={({ key }) => {
        if (key === 'logout') {
          handleLogout();
        }
      }}
      items={[
        {
          key: 'profile',
          label: `用户: ${user || 'admin'}`,
          icon: <UserOutlined />,
        },
        {
          key: 'logout',
          label: '退出登录',
          icon: <LogoutOutlined />,
        },
      ]}
    />
  );

  // 移动端菜单项定义
  const getMobileMenuItems = () => [
    { key: '/dashboard', icon: <BarChartOutlined />, label: '仪表盘' },
    { key: '/plugins', icon: <ApiOutlined />, label: '插件管理' },
    { key: '/config', icon: <SettingOutlined />, label: '配置管理' },
    { key: '/status', icon: <CloudSyncOutlined />, label: '状态监控' },
    { key: '/tools', icon: <ToolOutlined />, label: '工具' },
  ];

  // 移动端菜单点击处理
  const handleMobileMenuClick = (key: string) => {
    navigate(key);
    setMobileMenuOpen(false);
  };

  if (loading) {
    return (
      <div className="animated-bg" style={{ minHeight: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <div className="glass-card" style={{ padding: 32, width: 320, textAlign: 'center' }}>
          <div className="loading-spinner" style={{ margin: '0 auto 16px' }}></div>
          <h3>正在加载系统...</h3>
          <p style={{ color: 'var(--text-secondary)' }}>请稍候</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="animated-bg" style={{ minHeight: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', background: 'transparent' }}>
        <div className="glass-card" style={{ padding: 40, width: 380, borderRadius: 24, border: '1px solid rgba(255, 255, 255, 0.4)' }}>
          <div style={{ textAlign: 'center', marginBottom: 32 }}>
            <div className="tech-gradient" style={{ width: 72, height: 72, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px', boxShadow: '0 4px 12px rgba(24, 144, 255, 0.2)' }}>
              <AppstoreOutlined style={{ fontSize: 32, color: 'white' }} />
            </div>
            <h2 style={{ margin: 0, fontSize: 26, fontWeight: 600, color: 'var(--text-primary)' }}>欢迎回来</h2>
            <p style={{ color: 'var(--text-secondary)', margin: '8px 0 0', fontSize: 15 }}>Aggregator UI系统</p>
          </div>
          <Login />
        </div>
      </div>
    );
  }

  // 桌面端顶部导航菜单
  const desktopTopMenu = (
    <Menu
      mode="horizontal"
      selectedKeys={[location.pathname]}
      items={[{
        key: '/dashboard',
        icon: <HomeOutlined style={{ fontSize: 16 }} />,
        label: <Link to="/dashboard">首页</Link>
      }, {
        key: '/plugins',
        icon: <ApiOutlined style={{ fontSize: 16 }} />,
        label: <Link to="/plugins">插件</Link>
      }, {
        key: '/config',
        icon: <SettingOutlined style={{ fontSize: 16 }} />,
        label: <Link to="/config">配置</Link>
      }, {
        key: '/status',
        icon: <ProfileOutlined style={{ fontSize: 16 }} />,
        label: <Link to="/status">监控</Link>
      }]}
      style={{ background: 'transparent', borderBottom: 'none', minWidth: 400, fontWeight: 500 }}
    />
  );

  // 移动端底部导航
  const mobileBottomNav = (
    <div className="glass-card" style={{ position: 'fixed', bottom: 0, left: 0, right: 0, padding: '12px 0', zIndex: 1000 }}>
      <div style={{ display: 'flex', justifyContent: 'space-around' }}>
        {getMobileMenuItems().map(item => (
          <Button
            key={item.key}
            type={location.pathname === item.key ? 'primary' : 'text'}
            icon={item.icon}
            onClick={() => navigate(item.key)}
            style={{ flex: 1, border: 'none', borderRadius: 0 }}
          >
            {item.label}
          </Button>
        ))}
      </div>
    </div>
  );

  return (
    <div className="animated-bg" style={{ minHeight: '100vh', background: 'transparent' }}>
      {/* 移动端抽屉菜单 */}
      <Drawer
        placement="left"
        onClose={() => setMobileMenuOpen(false)}
        open={mobileMenuOpen}
        closable={true}
        width={240}
        bodyStyle={{ padding: 0 }}
      >
        <div className="glass-card" style={{ height: '100%', padding: 16 }}>
          <div style={{ marginBottom: 24, display: 'flex', alignItems: 'center', gap: 12 }}>
            <div className="tech-gradient" style={{ width: 40, height: 40, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <AppstoreOutlined style={{ fontSize: 20, color: 'white' }} />
            </div>
            <div>
              <div style={{ fontWeight: 600 }}>Aggregator UI系统</div>
              <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{user || '管理员'}</div>
            </div>
          </div>
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            onClick={({ key }) => handleMobileMenuClick(key)}
            items={getMobileMenuItems().map(item => ({
              key: item.key,
              icon: item.icon,
              label: item.label
            }))}
            style={{ background: 'transparent' }}
          />
        </div>
      </Drawer>

      {/* 桌面端头部 */}
      <Header className="glass-card" style={{ padding: '0 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', margin: '16px 16px 0', borderRadius: 20, border: '1px solid rgba(255, 255, 255, 0.4)', minHeight: 70 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <Button
            type="text"
            icon={<MenuOutlined />}
            onClick={() => setMobileMenuOpen(true)}
            className="mobile-menu-btn"
            style={{ fontSize: 18, width: 44, height: 44, borderRadius: 10 }}
          />
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div className="tech-gradient" style={{ width: 40, height: 40, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 4px 12px rgba(24, 144, 255, 0.2)' }}>
              <AppstoreOutlined style={{ fontSize: 20, color: 'white' }} />
            </div>
            <h1 style={{ margin: 0, fontSize: 22, fontWeight: 600, color: 'var(--text-primary)' }}>Aggregator UI系统</h1>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          {desktopTopMenu}
          <Dropdown overlay={userMenu} trigger={['click']}>
            <Button type="text" style={{ padding: '0 12px', borderRadius: 8 }}>
              <Space style={{ cursor: 'pointer' }}>
                <Avatar size="small" icon={<UserOutlined />} style={{ backgroundColor: '#1890ff' }} />
                <span style={{ fontSize: 14, color: 'var(--text-primary)' }}>{user || 'admin'}</span>
              </Space>
            </Button>
          </Dropdown>
        </div>
      </Header>

      <Layout style={{ margin: '16px', background: 'transparent', marginTop: 0 }}>
        <Layout style={{ background: 'transparent' }}>
          <Content className="glass-card" style={{ margin: 0, padding: 28, borderRadius: 24, minHeight: 500, border: '1px solid rgba(255, 255, 255, 0.4)' }}>
            <Routes>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/plugins" element={<PluginManager />} />
              <Route path="/config" element={<ConfigManager />} />
              <Route path="/status" element={<StatusMonitor />} />
              <Route path="/tools" element={<div>工具页面</div>} />
              <Route path="/" element={<Dashboard />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>

      {/* 移动端底部导航 - 仅在移动设备上显示 */}
      <div className="mobile-nav" style={{ display: 'none' }}>
        {mobileBottomNav}
      </div>

      <style>{`
        @media (max-width: 768px) {
          .mobile-menu-btn {
            display: block !important;
          }
          .mobile-nav {
            display: block !important;
          }
          .ant-layout {
            margin: 0 !important;
          }
          .glass-card {
            border-radius: 16px !important;
            margin: 8px;
          }
          .ant-drawer-content {
            background: transparent;
          }
          /* 移动端顶部菜单水平滚动 */
          .ant-menu-horizontal {
            overflow-x: auto;
            white-space: nowrap;
          }
          .ant-menu-item {
            margin-right: 8px;
          }
        }
        
        @media (min-width: 769px) {
          .mobile-menu-btn {
            display: none !important;
          }
          .ant-btn-text {
            border-radius: 8px;
          }
          /* 桌面端顶部菜单样式 */
          .ant-menu-horizontal {
            display: flex !important;
          }
          .ant-menu-item {
            margin-right: 0;
          }
        }
      `}</style>
    </div>
  );
};

export default AppContent;