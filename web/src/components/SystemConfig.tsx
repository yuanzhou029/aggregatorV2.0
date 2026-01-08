import React, { useState, useEffect } from 'react';
import { Card, Form, Input, Button, message, Tabs, Switch, Alert } from 'antd';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const { TabPane } = Tabs;

const SystemConfig: React.FC = () => {
  const [systemConfig, setSystemConfig] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [form] = Form.useForm();
  const { isAuthenticated } = useAuth(); // 使用认证状态

  useEffect(() => {
    if (isAuthenticated) { // 只有在认证后才获取配置
      fetchConfig();
    }
  }, [isAuthenticated]);

  const fetchConfig = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:5000/api/config/system');
      if (response.data.success) {
        setSystemConfig(response.data.data);
        form.setFieldsValue({
          env_vars: response.data.data.env_vars
        });
      }
    } catch (error) {
      console.error('获取系统配置失败:', error);
      message.error('获取系统配置失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      const values = form.getFieldsValue();
      
      // 验证必填字段
      const envVars = values.env_vars || {};
      if (!envVars.GIST_PAT || !envVars.GIST_LINK) {
        message.error('GIST_PAT 和 GIST_LINK 是必需的');
        return;
      }
      
      const response = await axios.put('http://localhost:5000/api/config/system', {
        env_vars: envVars
      });
      
      if (response.data.success) {
        message.success('系统配置已保存');
      } else {
        message.error(response.data.error || '保存失败');
      }
    } catch (error) {
      console.error('保存系统配置失败:', error);
      message.error('保存系统配置失败');
    } finally {
      setSaving(false);
    }
  };

  // 检查是否已认证，未认证时显示提示
  if (!isAuthenticated) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <h2>请先登录以访问系统配置功能</h2>
      </div>
    );
  }

  return (
    <div>
      <Card title="系统配置管理" style={{ marginBottom: 16 }}>
        <Alert
          message="系统配置"
          description="在此处配置系统环境变量，配置更改后需要重启服务才能完全生效"
          type="info"
          showIcon
        />
      </Card>
      <Card>
        <Form form={form} layout="vertical">
          <Tabs defaultActiveKey="env" type="card">
            <TabPane tab="环境变量" key="env">
              <Form.Item 
                label="GitHub Personal Access Token" 
                name={['env_vars', 'GIST_PAT']}
                help="用于访问GitHub Gist，需要gist权限"
              >
                <Input.Password placeholder="输入GitHub Personal Access Token" />
              </Form.Item>
              
              <Form.Item 
                label="Gist链接" 
                name={['env_vars', 'GIST_LINK']}
                help="格式：username/gist_id"
              >
                <Input placeholder="例如：yourusername/abc123def456" />
              </Form.Item>
              
              <Form.Item 
                label="自定义机场列表URL" 
                name={['env_vars', 'CUSTOMIZE_LINK']}
              >
                <Input placeholder="可选，自定义机场列表URL地址" />
              </Form.Item>
              
              <Form.Item 
                label="管理员用户名" 
                name={['env_vars', 'ADMIN_USERNAME']}
              >
                <Input placeholder="默认为admin" />
              </Form.Item>
              
              <Form.Item 
                label="管理员密码" 
                name={['env_vars', 'ADMIN_PASSWORD']}
                help="留空则不修改密码"
              >
                <Input.Password placeholder="输入新密码（留空则不修改）" />
              </Form.Item>
              
              <Form.Item 
                label="时区" 
                name={['env_vars', 'TZ']}
              >
                <Input placeholder="默认为Asia/Shanghai" />
              </Form.Item>
            </TabPane>
            
            <TabPane tab="系统信息" key="info">
              <div style={{ padding: '20px' }}>
                <h3>系统信息</h3>
                <p><strong>版本:</strong> {systemConfig.version || 'N/A'}</p>
                <p><strong>API端口:</strong> {systemConfig.api_port || 'N/A'}</p>
                <p><strong>Web端口:</strong> {systemConfig.web_port || 'N/A'}</p>
                <p><strong>存储类型:</strong> {systemConfig.storage_type || 'N/A'}</p>
              </div>
            </TabPane>
          </Tabs>
          
          <Form.Item>
            <Button type="primary" onClick={handleSave} loading={saving}>
              保存配置
            </Button>
            <Button style={{ marginLeft: 8 }} onClick={fetchConfig} disabled={loading}>
              重载配置
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default SystemConfig;