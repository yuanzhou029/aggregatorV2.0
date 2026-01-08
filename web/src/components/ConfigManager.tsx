import React, { useState, useEffect } from 'react';
import { Card, Form, Input, Button, message, Tabs, Switch } from 'antd';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const { TabPane } = Tabs;

interface PluginConfig {
  name: string;
  enabled: boolean;
  schedule: string;
  parameters: Record<string, any>;
}

const ConfigManager: React.FC = () => {
  const [pluginConfig, setPluginConfig] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [form] = Form.useForm();
  const { isAuthenticated } = useAuth(); // 使用认证状态

  useEffect(() => {
    if (isAuthenticated) { // 只有在认证后才获取配置
      fetchConfig();
    }
  }, [isAuthenticated]);

  const fetchConfig = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/config/plugin');
      if (response.data.success) {
        setPluginConfig(response.data.data);
        form.setFieldsValue(response.data.data);
      }
    } catch (error) {
      console.error('获取配置失败:', error);
      message.error('获取配置失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      const values = form.getFieldsValue();
      const response = await axios.put('http://localhost:5000/api/config/plugin', values);
      if (response.data.success) {
        message.success('配置已保存');
      } else {
        message.error(response.data.error || '保存失败');
      }
    } catch (error) {
      console.error('保存配置失败:', error);
      message.error('保存配置失败');
    }
  };

  // 检查是否已认证，未认证时显示提示
  if (!isAuthenticated) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <h2>请先登录以访问配置管理功能</h2>
      </div>
    );
  }

  return (
    <div>
      <Card title="配置管理" style={{ marginBottom: 16 }}>
        <p>管理系统配置和插件参数</p>
      </Card>
      <Card>
        <Form form={form} layout="vertical">
          <Tabs defaultActiveKey="plugins" type="card">
            <TabPane tab="插件配置" key="plugins">
              <Form.Item 
                label="插件配置" 
                name={['plugins']}
              >
                <Input.TextArea 
                  rows={20} 
                  placeholder="插件配置JSON" 
                  style={{ fontFamily: 'monospace' }}
                />
              </Form.Item>
              <Form.Item 
                label="插件配置预览" 
                name={['pluginsPreview']}
              >
                <div style={{ maxHeight: '300px', overflowY: 'auto', padding: '10px', border: '1px solid #d9d9d9', borderRadius: '4px', backgroundColor: '#f5f5f5' }}>
                  <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                    {JSON.stringify(form.getFieldValue(['plugins']), null, 2)}
                  </pre>
                </div>
              </Form.Item>
            </TabPane>
            <TabPane tab="系统配置" key="system">
              <Form.Item 
                label="系统配置" 
                name={['system']}
              >
                <Input.TextArea 
                  rows={20} 
                  placeholder="系统配置JSON" 
                  style={{ fontFamily: 'monospace' }}
                />
              </Form.Item>
            </TabPane>
          </Tabs>
          <Form.Item>
            <Button type="primary" onClick={handleSave}>
              保存配置
            </Button>
            <Button style={{ marginLeft: 8 }} onClick={fetchConfig}>
              重置
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default ConfigManager;