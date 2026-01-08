import React, { useState, useEffect } from 'react';
import { Card, Col, Row, Table, Tag, Button, Modal, Descriptions, Progress, Badge } from 'antd';
import axios from 'axios';
import { CheckCircleOutlined, SyncOutlined, ClockCircleOutlined, AppstoreOutlined, ThunderboltOutlined } from '@ant-design/icons';

interface Plugin {
  name: string;
  description: string;
  enabled: boolean;
  cron_schedule: string;
  last_run?: string;
  next_run?: string;
  status: string;
  parameters: Record<string, any>;
  timeout: number;
  max_retries: number;
}

interface SystemStatus {
  total_plugins: number;
  active_plugins: number;
  running_tasks: number;
  system_uptime: string;
}

const Dashboard: React.FC = () => {
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPlugin] = useState<Plugin | null>(null);
  const [modalVisible, setModalVisible] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [pluginsResponse, statusResponse] = await Promise.all([
        axios.get('http://localhost:5000/api/plugins'),
        axios.get('http://localhost:5000/api/status')
      ]);

      // 处理插件数据
      if (pluginsResponse.data.success) {
        setPlugins(pluginsResponse.data.data || []);
      } else {
        console.error('获取插件列表失败:', pluginsResponse.data.error);
        setPlugins([]);
      }
      
      // 处理状态数据
      if (statusResponse.data.success) {
        setStatus(statusResponse.data.data);
      } else {
        console.error('获取状态失败:', statusResponse.data.error);
        setStatus({
          total_plugins: 0,
          active_plugins: 0,
          running_tasks: 0,
          system_uptime: 'N/A'
        });
      }
    } catch (error) {
      console.error('获取数据失败:', error);
    } finally {
      setLoading(false);
    }
  };



  const getStatusColor = (enabled: boolean) => {
    return enabled ? 'success' : 'default';
  };

  const columns = [
    {
      title: '插件名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <Badge status={getStatusColor(true)} text={text} />,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '状态',
      key: 'status',
      render: (record: Plugin) => (
        <Tag color={record.enabled ? 'green' : 'red'}>
          {record.enabled ? '启用' : '禁用'}
        </Tag>
      ),
    },
    {
      title: '定时任务',
      dataIndex: 'cron_schedule',
      key: 'cron_schedule',
      render: (text: string) => text || '-',
    },
    {
      title: '最后运行',
      dataIndex: 'last_run',
      key: 'last_run',
      render: (text: string) => text || '-',
    },
    {
      title: '下次运行',
      dataIndex: 'next_run',
      key: 'next_run',
      render: (text: string) => text || '-',
    },
    {
      title: '运行状态',
      key: 'run_status',
      render: (record: Plugin) => (
        <Tag color={record.status === 'error' ? 'red' : 'blue'}>
          {record.status === 'error' ? '运行失败' : record.status || '正常'}
        </Tag>
      ),
    },
  ];

  return (
    <div>
      <Row gutter={[24, 24]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card className="glass-card floating-element" style={{ borderRadius: 20, height: 130, border: '1px solid rgba(255, 255, 255, 0.4)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16, height: '100%' }}>
              <div className="tech-gradient" style={{ width: 52, height: 52, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <AppstoreOutlined style={{ fontSize: 26, color: 'white' }} />
              </div>
              <div style={{ flexGrow: 1 }}>
                <div style={{ fontSize: 15, color: 'var(--text-secondary)', marginBottom: 4 }}>插件总数</div>
                <div style={{ fontSize: 26, fontWeight: 600, color: 'var(--text-primary)' }}>{status?.total_plugins || 0}</div>
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="glass-card floating-element" style={{ borderRadius: 20, height: 130, border: '1px solid rgba(255, 255, 255, 0.4)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16, height: '100%' }}>
              <div className="tech-gradient" style={{ width: 52, height: 52, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #52c41a 0%, #389e0d 100%)', flexShrink: 0 }}>
                <CheckCircleOutlined style={{ fontSize: 26, color: 'white' }} />
              </div>
              <div style={{ flexGrow: 1 }}>
                <div style={{ fontSize: 15, color: 'var(--text-secondary)', marginBottom: 4 }}>活跃插件</div>
                <div style={{ fontSize: 26, fontWeight: 600, color: 'var(--text-primary)' }}>{status?.active_plugins || 0}</div>
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="glass-card floating-element" style={{ borderRadius: 20, height: 130, border: '1px solid rgba(255, 255, 255, 0.4)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16, height: '100%' }}>
              <div className="tech-gradient" style={{ width: 52, height: 52, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #faad14 0%, #fa8c16 100%)', flexShrink: 0 }}>
                <ThunderboltOutlined style={{ fontSize: 26, color: 'white' }} />
              </div>
              <div style={{ flexGrow: 1 }}>
                <div style={{ fontSize: 15, color: 'var(--text-secondary)', marginBottom: 4 }}>运行任务</div>
                <div style={{ fontSize: 26, fontWeight: 600, color: 'var(--text-primary)' }}>{status?.running_tasks || 0}</div>
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="glass-card floating-element" style={{ borderRadius: 20, height: 130, border: '1px solid rgba(255, 255, 255, 0.4)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16, height: '100%' }}>
              <div className="tech-gradient" style={{ width: 52, height: 52, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #722ed1 0%, #531dab 100%)', flexShrink: 0 }}>
                <ClockCircleOutlined style={{ fontSize: 26, color: 'white' }} />
              </div>
              <div style={{ flexGrow: 1 }}>
                <div style={{ fontSize: 15, color: 'var(--text-secondary)', marginBottom: 4 }}>系统运行时间</div>
                <div style={{ fontSize: 26, fontWeight: 600, color: 'var(--text-primary)' }}>{status?.system_uptime || 0}</div>
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      <Row gutter={[24, 24]}>
        <Col xs={24} lg={16}>
          <Card className="glass-card" style={{ borderRadius: 20, border: '1px solid rgba(255, 255, 255, 0.4)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h3 style={{ margin: 0, fontWeight: 600, fontSize: 18, color: 'var(--text-primary)' }}>插件列表</h3>
              <Button type="primary" onClick={fetchData} icon={<SyncOutlined />} style={{ borderRadius: 8, fontWeight: 500 }}>刷新</Button>
            </div>
            <Table
              columns={columns}
              dataSource={plugins}
              rowKey="name"
              loading={loading}
              pagination={{ pageSize: 8, showSizeChanger: false }}
              scroll={{ y: 400 }}
              size="middle"
            />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card className="glass-card" style={{ borderRadius: 20, height: 'fit-content', border: '1px solid rgba(255, 255, 255, 0.4)' }}>
            <h3 style={{ margin: '0 0 16px', fontWeight: 600, fontSize: 18, color: 'var(--text-primary)' }}>系统概览</h3>
            <div style={{ marginBottom: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span style={{ color: 'var(--text-secondary)' }}>插件启用率</span>
                <span style={{ fontWeight: 500 }}>{status?.active_plugins && status?.total_plugins ? Math.round((status.active_plugins / status.total_plugins) * 100) : 0}%</span>
              </div>
              <Progress 
                percent={status?.active_plugins && status?.total_plugins ? Math.round((status.active_plugins / status.total_plugins) * 100) : 0} 
                strokeColor="#1890ff" 
                showInfo={false}
              />
            </div>
            <div style={{ marginBottom: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span style={{ color: 'var(--text-secondary)' }}>任务运行率</span>
                <span style={{ fontWeight: 500 }}>{status?.running_tasks && status?.active_plugins ? Math.round((status.running_tasks / status.active_plugins) * 100) : 0}%</span>
              </div>
              <Progress 
                percent={status?.running_tasks && status?.active_plugins ? Math.round((status.running_tasks / status.active_plugins) * 100) : 0} 
                strokeColor="#52c41a" 
                showInfo={false}
              />
            </div>
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              <div className="glass-card" style={{ padding: 16, borderRadius: 16, flex: 1, minWidth: 100, border: '1px solid rgba(255, 255, 255, 0.4)' }}>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 4 }}>总插件数</div>
                <div style={{ fontSize: 20, fontWeight: 600, color: 'var(--text-primary)' }}>{status?.total_plugins || 0}</div>
              </div>
              <div className="glass-card" style={{ padding: 16, borderRadius: 16, flex: 1, minWidth: 100, border: '1px solid rgba(255, 255, 255, 0.4)' }}>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 4 }}>活跃插件</div>
                <div style={{ fontSize: 20, fontWeight: 600, color: 'var(--text-primary)' }}>{status?.active_plugins || 0}</div>
              </div>
              <div className="glass-card" style={{ padding: 16, borderRadius: 16, flex: 1, minWidth: 100, border: '1px solid rgba(255, 255, 255, 0.4)' }}>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 4 }}>运行中</div>
                <div style={{ fontSize: 20, fontWeight: 600, color: 'var(--text-primary)' }}>{status?.running_tasks || 0}</div>
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      <Modal
        title={`插件详情 - ${selectedPlugin?.name}`}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={850}
        className="glass-card"
        style={{ borderRadius: 20 }}
        bodyStyle={{ padding: 24 }}
      >
        {selectedPlugin && (
          <Descriptions column={2} bordered size="middle">
            <Descriptions.Item label="插件名称">{selectedPlugin.name}</Descriptions.Item>
            <Descriptions.Item label="描述">{selectedPlugin.description}</Descriptions.Item>
            <Descriptions.Item label="启用状态">
              <Tag color={selectedPlugin.enabled ? 'green' : 'red'} style={{ borderRadius: 6, fontWeight: 500 }}>
                {selectedPlugin.enabled ? '启用' : '禁用'}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="运行状态">
              <Tag color={selectedPlugin.status === 'error' ? 'red' : 'blue'} style={{ borderRadius: 6, fontWeight: 500 }}>
                {selectedPlugin.status === 'error' ? '运行失败' : selectedPlugin.status || '正常'}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="定时任务">{selectedPlugin.cron_schedule || '-'}</Descriptions.Item>
            <Descriptions.Item label="最后运行">{selectedPlugin.last_run || '-'}</Descriptions.Item>
            <Descriptions.Item label="下次运行">{selectedPlugin.next_run || '-'}</Descriptions.Item>
            <Descriptions.Item label="超时时间">{selectedPlugin.timeout}秒</Descriptions.Item>
            <Descriptions.Item label="最大重试次数">{selectedPlugin.max_retries}</Descriptions.Item>
            <Descriptions.Item label="参数" span={2}>
              <pre style={{ background: 'var(--card-bg)', padding: 16, borderRadius: 10, maxHeight: 200, overflow: 'auto', fontSize: 13, border: '1px solid rgba(0, 0, 0, 0.06)' }}>{JSON.stringify(selectedPlugin.parameters, null, 2)}</pre>
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  );
};

export default Dashboard;