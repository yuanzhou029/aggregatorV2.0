import React, { useState, useEffect } from 'react';
import { Card, Tabs, Form, Input, Button, message, Row, Col, Select } from 'antd';
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

// 配置axios拦截器自动添加认证头
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

interface SystemConfig {
  version: string;
  api_port: number;
  web_port: number;
  storage_type: string;
  env_vars: {
    GIST_PAT: string;
    GIST_LINK: string;
    CUSTOMIZE_LINK: string;
    ADMIN_USERNAME: string;
    TZ: string;
    ADMIN_PASSWORD?: string;
    API_PORT?: number;
    WEB_PORT?: number;
  };
}

interface PluginConfig {
  plugins: Record<string, any>;
}

const ConfigManager: React.FC = () => {
  const [, setSystemConfig] = useState<SystemConfig | null>(null);
  const [, setPluginConfig] = useState<PluginConfig | null>(null);
  const [activeTab, setActiveTab] = useState('system');
  const [systemForm] = Form.useForm();
  const [loading, setLoading] = useState(true);
  const { isAuthenticated } = useAuth();

  // 从systemConfig中获取当前的API端口和Web端口，用于显示在UI上

  useEffect(() => {
    if (isAuthenticated) {
      loadConfigs();
    }
  }, [isAuthenticated]);

  const loadConfigs = async () => {
    try {
      setLoading(true);
      
      // 加载系统配置
      const systemResponse = await axios.get('http://localhost:5000/api/config/system');
      if (systemResponse.data.success) {
        setSystemConfig(systemResponse.data.data);
        systemForm.setFieldsValue(systemResponse.data.data);
      }
      
      // 加载插件配置
      const pluginResponse = await axios.get('http://localhost:5000/api/config/plugin');
      if (pluginResponse.data.success) {
        setPluginConfig(pluginResponse.data.data);
      }
    } catch (error) {
      console.error('加载配置失败:', error);
      message.error('加载配置失败');
    } finally {
      setLoading(false);
    }
  };

  const saveSystemConfig = async () => {
    try {
      const values = await systemForm.validateFields();
      const response = await axios.put('http://localhost:5000/api/config/system', values);
      if (response.data.success) {
        message.success('系统配置已保存');
        loadConfigs(); // 重新加载配置
      } else {
        message.error(response.data.error || '保存配置失败');
      }
    } catch (error) {
      console.error('保存系统配置失败:', error);
      message.error('保存配置失败');
    }
  };

  if (!isAuthenticated) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <h2>请先登录以访问配置管理功能</h2>
      </div>
    );
  }

  return (
    <div>
      <Card className="glass-card" title="系统配置管理" style={{ marginBottom: 24, borderRadius: 20, border: '1px solid rgba(255, 255, 255, 0.4)' }}>
        <p style={{ color: 'var(--text-secondary)' }}>管理系统的各项配置参数，按功能分类进行可视化编辑</p>
      </Card>
      
      <Card className="glass-card" style={{ borderRadius: 20, border: '1px solid rgba(255, 255, 255, 0.4)' }}>
        <Tabs 
          activeKey={activeTab} 
          onChange={setActiveTab}
          items={[
            {
              key: 'system',
              label: '系统配置',
              children: (
                <div>
                  <Row justify="end" style={{ marginBottom: 16 }}>
                    <Col>
                      <Button 
                        icon={<ReloadOutlined />} 
                        onClick={loadConfigs}
                        style={{ marginRight: 8, borderRadius: 6 }}
                      >
                        刷新
                      </Button>
                      <Button 
                        type="primary" 
                        icon={<SaveOutlined />} 
                        onClick={saveSystemConfig}
                        style={{ borderRadius: 6, fontWeight: 500 }}
                      >
                        保存配置
                      </Button>
                    </Col>
                  </Row>
                  
                  <Form 
                    form={systemForm} 
                    layout="vertical" 
                    disabled={loading}
                  >
                    <Row gutter={16}>
                      <Col span={12}>
                        <Form.Item
                          label="API端口"
                          name={['env_vars', 'API_PORT']}
                        >
                          <Input placeholder="API服务端口" type="number" style={{ borderRadius: 6 }} />
                        </Form.Item>
                      </Col>
                      <Col span={12}>
                        <Form.Item
                          label="Web端口"
                          name={['env_vars', 'WEB_PORT']}
                        >
                          <Input placeholder="前端服务端口" type="number" style={{ borderRadius: 6 }} />
                        </Form.Item>
                      </Col>
                    </Row>
                    
                    <Form.Item
                      label="管理员用户名"
                      name={['env_vars', 'ADMIN_USERNAME']}
                    >
                      <Input placeholder="管理员用户名" style={{ borderRadius: 6 }} />
                    </Form.Item>
                    
                    <Form.Item
                      label="管理员密码"
                      name={['env_vars', 'ADMIN_PASSWORD']}
                    >
                      <Input.Password placeholder="留空则不修改密码" style={{ borderRadius: 6 }} />
                    </Form.Item>
                    
                    <Form.Item
                      label="Gist个人访问令牌(PAT)"
                      name={['env_vars', 'GIST_PAT']}
                    >
                      <Input.TextArea 
                        rows={3} 
                        placeholder="GitHub Gist个人访问令牌，用于同步配置" 
                        style={{ borderRadius: 6 }}
                      />
                    </Form.Item>
                    
                    <Form.Item
                      label="Gist链接"
                      name={['env_vars', 'GIST_LINK']}
                    >
                      <Input placeholder="Gist链接地址" style={{ borderRadius: 6 }} />
                    </Form.Item>
                    
                    <Form.Item
                      label="自定义链接"
                      name={['env_vars', 'CUSTOMIZE_LINK']}
                    >
                      <Input placeholder="自定义配置链接" style={{ borderRadius: 6 }} />
                    </Form.Item>
                    
                    <Form.Item
                      label="时区"
                      name={['env_vars', 'TZ']}
                    >
                      <Select placeholder="请选择时区" style={{ borderRadius: 6 }}>
                        <Select.Option value="Asia/Shanghai">亚洲/上海</Select.Option>
                        <Select.Option value="UTC">UTC</Select.Option>
                        <Select.Option value="America/New_York">美洲/纽约</Select.Option>
                        <Select.Option value="Europe/London">欧洲/伦敦</Select.Option>
                      </Select>
                    </Form.Item>
                    
                    <Form.Item
                      label="存储类型"
                      name="storage_type"
                    >
                      <Select style={{ borderRadius: 6 }}>
                        <Select.Option value="local">本地存储</Select.Option>
                        <Select.Option value="gist">Gist存储</Select.Option>
                      </Select>
                    </Form.Item>
                  </Form>
                </div>
              ),
            },
            {
              key: 'plugins',
              label: '插件配置',
              children: (
                <div>
                  <p style={{ color: 'var(--text-secondary)' }}>插件配置将在插件管理界面进行可视化编辑</p>
                  <p style={{ color: 'var(--text-secondary)' }}>点击左侧导航栏的"插件管理"进入插件配置界面</p>
                </div>
              ),
            },
            {
              key: 'subscription',
              label: '订阅配置',
              children: (
                <div>
                  <p style={{ color: 'var(--text-secondary)' }}>订阅配置管理</p>
                  <p style={{ color: 'var(--text-secondary)' }}>(此部分将根据实际需求扩展)</p>
                </div>
              ),
            },
            {
              key: 'advanced',
              label: '高级配置',
              children: (
                <div>
                  <p style={{ color: 'var(--text-secondary)' }}>高级系统配置</p>
                  <p style={{ color: 'var(--text-secondary)' }}>(此部分将根据实际需求扩展)</p>
                </div>
              ),
            }
          ]}
        />
      </Card>
    </div>
  );
};

export default ConfigManager;