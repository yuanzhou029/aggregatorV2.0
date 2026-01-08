import React, { useState } from 'react';
import { LockOutlined, UserOutlined, LoadingOutlined } from '@ant-design/icons';
import { Button, Form, Input, message, Typography } from 'antd';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const { Text } = Typography;

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      const success = await login(values.username, values.password);
      if (success) {
        message.success('登录成功');
        navigate('/dashboard');
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
    <div style={{ width: '100%' }}>
      <Form
        name="login"
        initialValues={{ remember: true }}
        onFinish={onFinish}
        autoComplete="off"
        layout="vertical"
      >
        <Form.Item
          label="用户名"
          name="username"
          rules={[{ required: true, message: '请输入用户名!' }]}
        >
          <Input 
            prefix={<UserOutlined />} 
            placeholder="请输入用户名" 
            size="large"
            style={{ borderRadius: 10, height: 48, fontSize: 15 }}
          />
        </Form.Item>

        <Form.Item
          label="密码"
          name="password"
          rules={[{ required: true, message: '请输入密码!' }]}
        >
          <Input.Password 
            prefix={<LockOutlined />} 
            placeholder="请输入密码" 
            size="large"
            style={{ borderRadius: 10, height: 48, fontSize: 15 }}
          />
        </Form.Item>

        <Form.Item>
          <Button 
            type="primary" 
            htmlType="submit" 
            loading={loading}
            block
            size="large"
            style={{ 
              height: 48, 
              borderRadius: 10,
              background: 'linear-gradient(135deg, #1890ff 0%, #52c41a 100%)',
              border: 'none',
              fontWeight: 500,
              fontSize: 16
            }}
            icon={loading ? <LoadingOutlined /> : null}
          >
            {loading ? '登录中...' : '登录'}
          </Button>
        </Form.Item>
        
        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <Text type="secondary" style={{ fontSize: 12 }}>
          </Text>
        </div>
      </Form>
    </div>
  );
};

export default Login;