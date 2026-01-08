import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Switch, Tag, Space, message } from 'antd';
import { PlayCircleOutlined, StopOutlined, ReloadOutlined } from '@ant-design/icons';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

interface Plugin {
  name: string;
  description: string;
  enabled: boolean;
  status: string;
  schedule: string;
  parameters: Record<string, any>;
  lastRun?: string;
  nextRun?: string;
}

const PluginManager: React.FC = () => {
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [loading, setLoading] = useState(true);
  const { isAuthenticated } = useAuth(); // 使用认证状态

  useEffect(() => {
    if (isAuthenticated) { // 只有在认证后才获取插件列表
      fetchPlugins();
    }
  }, [isAuthenticated]);

  const fetchPlugins = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:5000/api/plugins');
      if (response.data.success) {
        setPlugins(response.data.data);
      }
    } catch (error) {
      console.error('获取插件列表失败:', error);
      message.error('获取插件列表失败');
    } finally {
      setLoading(false);
    }
  };

  const togglePlugin = async (pluginName: string, enabled: boolean) => {
    try {
      const response = enabled 
        ? await axios.post(`http://localhost:5000/api/plugins/${pluginName}/enable`)
        : await axios.post(`http://localhost:5000/api/plugins/${pluginName}/disable`);
      
      if (response.data.success) {
        message.success(enabled ? '插件已启用' : '插件已禁用');
        fetchPlugins(); // 刷新列表
      } else {
        message.error(response.data.error || '操作失败');
      }
    } catch (error) {
      console.error('操作插件失败:', error);
      message.error('操作插件失败');
    }
  };

  const runPlugin = async (pluginName: string) => {
    try {
      const response = await axios.post(`http://localhost:5000/api/plugins/${pluginName}/run`);
      if (response.data.success) {
        message.success('插件已启动执行');
      } else {
        message.error(response.data.error || '执行失败');
      }
    } catch (error) {
      console.error('执行插件失败:', error);
      message.error('执行插件失败');
    }
  };

  // 检查是否已认证，未认证时显示提示
  if (!isAuthenticated) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <h2>请先登录以访问插件管理功能</h2>
      </div>
    );
  }

  const columns = [
    {
      title: '插件名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '状态',
      key: 'status',
      render: (text: any, record: Plugin) => (
        <Tag color={record.status === 'running' ? 'green' : 'default'}>
          {record.status}
        </Tag>
      ),
    },
    {
      title: '启用',
      key: 'enabled',
      render: (text: any, record: Plugin) => (
        <Switch
          checked={record.enabled}
          onChange={(checked) => togglePlugin(record.name, checked)}
        />
      ),
    },
    {
      title: '定时配置',
      dataIndex: 'schedule',
      key: 'schedule',
    },
    {
      title: '操作',
      key: 'action',
      render: (text: any, record: Plugin) => (
        <Space size="middle">
          <Button 
            type="primary" 
            icon={<PlayCircleOutlined />} 
            onClick={() => runPlugin(record.name)}
            disabled={!record.enabled}
          >
            运行
          </Button>
          <Button 
            icon={<ReloadOutlined />} 
            onClick={fetchPlugins}
          >
            刷新
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card title="插件管理" style={{ marginBottom: 16 }}>
        <p>管理插件的启用状态、执行和配置</p>
      </Card>
      <Card>
        <Table 
          columns={columns} 
          dataSource={plugins} 
          rowKey="name"
          loading={loading}
        />
      </Card>
    </div>
  );
};

export default PluginManager;