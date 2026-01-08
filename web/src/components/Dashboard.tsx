import React from 'react';
import { Card, Row, Col, Statistic, Space } from 'antd';
import { AppstoreOutlined, CheckCircleOutlined, ClockCircleOutlined, WarningOutlined } from '@ant-design/icons';
import axios from 'axios';

const Dashboard: React.FC = () => {
  // 模拟数据，实际应该从API获取
  const statsData = {
    totalPlugins: 8,
    activePlugins: 5,
    totalExecutions: 120,
    lastUpdate: '2023-12-19 10:30:45'
  };

  return (
    <div>
      <Card title="系统概览" style={{ marginBottom: 16 }}>
        <p>Aggregator 系统运行状态总览</p>
      </Card>
      
      <Row gutter={16}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总插件数"
              value={statsData.totalPlugins}
              prefix={<AppstoreOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="活跃插件"
              value={statsData.activePlugins}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总执行次数"
              value={statsData.totalExecutions}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="最近更新"
              value={statsData.lastUpdate}
              prefix={<WarningOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card title="系统信息" style={{ marginTop: 16 }}>
        <Space direction="vertical" size="middle" style={{ display: 'flex' }}>
          <p><strong>版本:</strong> Aggregator UI v1.0.0</p>
          <p><strong>状态:</strong> <span style={{ color: '#52c41a' }}>运行中</span></p>
          <p><strong>API连接:</strong> <span style={{ color: '#52c41a' }}>已连接</span></p>
        </Space>
      </Card>
    </div>
  );
};

export default Dashboard;