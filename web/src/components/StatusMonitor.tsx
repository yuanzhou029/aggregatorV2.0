import React, { useState, useEffect } from 'react';
import { Card, Table, Statistic, Row, Col, Spin, Button } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
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

interface StatusData {
  total_plugins: number;
  active_plugins: number;
  last_update: string;
  plugins: Array<{
    name: string;
    description: string;
    enabled: boolean;
    status: string;
    schedule: string;
  }>;
}

const StatusMonitor: React.FC = () => {
  const [statusData, setStatusData] = useState<StatusData | null>(null);
  const [loading, setLoading] = useState(true);
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      fetchStatus();
    }
  }, [isAuthenticated]);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:5000/api/status');
      if (response.data.success) {
        setStatusData(response.data.data);
      }
    } catch (error) {
      console.error('获取状态失败:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <h2>请先登录以访问状态监控功能</h2>
      </div>
    );
  }

  const columns = [
    {
      title: '插件名称',
      dataIndex: 'name',
      key: 'name',
      width: '15%',
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      width: '30%',
    },
    {
      title: '启用',
      dataIndex: 'enabled',
      key: 'enabled',
      width: '10%',
      render: (enabled: boolean) => (
        <span style={{ fontWeight: 500, color: enabled ? 'var(--secondary-color)' : 'var(--text-tertiary)' }}>{enabled ? '是' : '否'}</span>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: '15%',
      render: (status: string) => (
        <span style={{ fontWeight: 500, color: status === 'running' ? 'var(--secondary-color)' : status === 'error' ? '#ff4d4f' : 'var(--text-tertiary)' }}>{status || '空闲'}</span>
      ),
    },
    {
      title: '定时配置',
      dataIndex: 'schedule',
      key: 'schedule',
      width: '30%',
    },
  ];

  return (
    <div>
      <Card className="glass-card" title="系统状态监控" style={{ marginBottom: 24, borderRadius: 20, border: '1px solid rgba(255, 255, 255, 0.4)' }}>
        <p style={{ color: 'var(--text-secondary)' }}>实时监控系统运行状态和插件执行情况</p>
      </Card>
      
      <Row gutter={24} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card className="glass-card" style={{ borderRadius: 20, border: '1px solid rgba(255, 255, 255, 0.4)' }}>
            <Statistic
              title="总插件数"
              value={statusData?.total_plugins || 0}
              loading={loading}
              valueStyle={{ fontSize: 24, fontWeight: 600, color: 'var(--text-primary)' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="glass-card" style={{ borderRadius: 20, border: '1px solid rgba(255, 255, 255, 0.4)' }}>
            <Statistic
              title="活跃插件"
              value={statusData?.active_plugins || 0}
              loading={loading}
              valueStyle={{ fontSize: 24, fontWeight: 600, color: 'var(--text-primary)' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="glass-card" style={{ borderRadius: 20, border: '1px solid rgba(255, 255, 255, 0.4)' }}>
            <Statistic
              title="最后更新"
              value={statusData?.last_update ? new Date(statusData.last_update).toLocaleString() : '-'}
              loading={loading}
              valueStyle={{ fontSize: 16, fontWeight: 500, color: 'var(--text-primary)' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="glass-card" style={{ borderRadius: 20, height: '100%', border: '1px solid rgba(255, 255, 255, 0.4)' }}>
            <Button 
              icon={<ReloadOutlined />} 
              onClick={fetchStatus}
              loading={loading}
              block
              style={{ borderRadius: 8, fontWeight: 500, height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
            >
              刷新状态
            </Button>
          </Card>
        </Col>
      </Row>
      
      <Card className="glass-card" title="插件详情" style={{ borderRadius: 20, border: '1px solid rgba(255, 255, 255, 0.4)' }}>
        <Spin spinning={loading}>
          <Table 
            columns={columns} 
            dataSource={statusData?.plugins || []} 
            rowKey="name"
            pagination={{ pageSize: 10, showSizeChanger: false }}
            size="middle"
          />
        </Spin>
      </Card>
    </div>
  );
};

export default StatusMonitor;