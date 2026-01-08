import React, { useState } from 'react';
import { LockOutlined, UserOutlined } from '@ant-design/icons';
import { Button, Card, Form, Input, message } from 'antd';
import { useAuth } from '../contexts/AuthContext';

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      const success = await login(values.username, values.password);
      if (success) {
        message.success('登录成功');
        // 登录成功后，由路由守卫处理跳转
      } else {
        message.error('用户名或密码错误');
      }
    } catch (error) {
      message.error('登录失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', backgroundColor: '#f0f2f5' }}>
      <Card title="Aggregator 管理系统登录" style={{ width: 400 }}>
        <Form
          name="login"
          initialValues={{ remember: true }}
          onFinish={onFinish}
          autoComplete="off"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名!' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码!' }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" style={{ width: '100%' }} loading={loading}>
              登录
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Login;