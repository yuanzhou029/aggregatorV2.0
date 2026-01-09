import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Switch, Tag, Space, message, Modal, Form, Input, Upload, Tabs, Alert, Popconfirm } from 'antd';
import { PlayCircleOutlined, ReloadOutlined, PlusOutlined, DeleteOutlined, UploadOutlined, EditOutlined, FileTextOutlined } from '@ant-design/icons';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

// 配置axios拦截器自动添加认证头
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    } else {
      console.warn('No authentication token found');
    }
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

interface Plugin {
  name: string;
  description: string;
  enabled: boolean;
  status: string;
  schedule: string;
  parameters: Record<string, any>;
  module_path?: string;
  function_name?: string;
  lastRun?: string;
  nextRun?: string;
}

interface AddPluginFormValues {
  name: string;
  description: string;
  enabled: boolean;
  schedule: string;
  parameters: Record<string, any>;
  upload?: UploadedFileInfo[];
}

interface EditPluginFormValues {
  description: string;
  enabled: boolean;
  schedule: string;
  parameters: Record<string, any>;
}

interface UploadedFileInfo {
  uid: string;
  name: string;
  status: 'done' | 'error' | 'uploading' | 'removed';
  url?: string;
  originFileObj?: File;
}

const PluginManager: React.FC = () => {
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [configModalVisible, setConfigModalVisible] = useState(false);
  const [editingPlugin, setEditingPlugin] = useState<Plugin | null>(null);
  const [editingConfig, setEditingConfig] = useState<string>('');
  const [configTabActiveKey, setConfigTabActiveKey] = useState('json');
  const [form] = Form.useForm();
  const [editForm] = Form.useForm();
  const { isAuthenticated } = useAuth(); // 使用认证状态

  useEffect(() => {
    if (isAuthenticated) { // 只有在认证后才获取插件列表
      fetchPlugins();
    }
  }, [isAuthenticated]);

  const fetchPlugins = async () => {
    try {
      setLoading(true);
      
      // 检查认证令牌
      const token = localStorage.getItem('authToken');
      if (!token) {
        message.error('认证令牌缺失，请重新登录');
        return;
      }
      
      const response = await axios.get('http://localhost:5000/api/plugins');
      if (response.data.success) {
        setPlugins(response.data.data);
      } else {
        message.error(response.data.error || '获取插件列表失败');
      }
    } catch (error: any) {
      console.error('获取插件列表失败:', error);
      
      // 检查错误类型并给出更具体的错误信息
      if (error.response) {
        // 服务器响应了错误状态码
        if (error.response.status === 401) {
          message.error('认证失败，请重新登录');
        } else if (error.response.status === 403) {
          message.error('权限不足，无法获取插件列表');
        } else {
          message.error(`获取插件列表失败: ${error.response.data?.error || error.response.statusText}`);
        }
      } else if (error.request) {
        // 请求已发出但没有收到响应
        message.error('无法连接到服务器，请检查后端服务是否运行');
      } else {
        // 其他错误
        message.error(`获取插件列表失败: ${error.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchPluginConfig = async (pluginName: string) => {
    try {
      // 检查认证令牌
      const token = localStorage.getItem('authToken');
      if (!token) {
        message.error('认证令牌缺失，请重新登录');
        return '';
      }
      
      const response = await axios.get('http://localhost:5000/api/config/plugin');
      if (response.data.success) {
        const pluginConfig = response.data.data.plugins?.[pluginName];
        if (pluginConfig) {
          return JSON.stringify(pluginConfig, null, 2);
        }
      } else {
        message.error(response.data.error || '获取插件配置失败');
      }
    } catch (error: any) {
      console.error('获取插件配置失败:', error);
      
      // 检查错误类型并给出更具体的错误信息
      if (error.response) {
        // 服务器响应了错误状态码
        if (error.response.status === 401) {
          message.error('认证失败，请重新登录');
        } else if (error.response.status === 403) {
          message.error('权限不足，无法获取插件配置');
        } else {
          message.error(`获取插件配置失败: ${error.response.data?.error || error.response.statusText}`);
        }
      } else if (error.request) {
        // 请求已发出但没有收到响应
        message.error('无法连接到服务器，请检查后端服务是否运行');
      } else {
        // 其他错误
        message.error(`获取插件配置失败: ${error.message}`);
      }
    }
    return '';
  };

  const addPlugin = async (values: AddPluginFormValues) => {
    try {
      // 检查认证令牌
      const token = localStorage.getItem('authToken');
      if (!token) {
        message.error('认证令牌缺失，请重新登录');
        return;
      }
      
      console.log('开始添加插件，参数:', values);
      
      // 检查是否有上传的文件
      if (values.upload && Array.isArray(values.upload) && values.upload.length > 0) {
        const fileInfo = values.upload[0];
        const file = fileInfo.originFileObj;
        
        if (file) {
          console.log('上传文件模式:', file.name);
          // 创建FormData来上传文件
          const formData = new FormData();
          formData.append('file', file);
          formData.append('name', values.name);
          formData.append('description', values.description);
          formData.append('module_path', `subscribe.scripts.${values.name}`); // 自动生成模块路径
          formData.append('function_name', 'main'); // 默认函数名
          formData.append('enabled', String(values.enabled));
          formData.append('schedule', values.schedule);
          formData.append('parameters', JSON.stringify(values.parameters || {}));
          
          const response = await axios.post('http://localhost:5000/api/plugins/upload', formData);
          
          console.log('上传插件响应:', response.data);
          if (response.data.success) {
            message.success(response.data.message);
            setModalVisible(false);
            form.resetFields();
            fetchPlugins(); // 刷新列表
            return;
          } else {
            message.error(response.data.error || '上传插件失败');
            return;
          }
        }
      }
      
      console.log('添加配置模式');
      // 如果没有上传文件，只是添加配置
      const response = await axios.post('http://localhost:5000/api/plugins/add', {
        name: values.name,
        description: values.description,
        module_path: `subscribe.scripts.${values.name}`, // 自动生成模块路径
        function_name: 'main', // 默认函数名
        enabled: values.enabled,
        schedule: values.schedule,
        parameters: values.parameters
      });
      
      console.log('添加插件响应:', response.data);
      if (response.data.success) {
        message.success(response.data.message);
        setModalVisible(false);
        form.resetFields();
        fetchPlugins(); // 刷新列表
      } else {
        message.error(response.data.error || '添加插件失败');
      }
    } catch (err: any) {
      console.error('添加插件失败:', err);
      
      // 检查错误类型并给出更具体的错误信息
      if (err.response) {
        // 服务器响应了错误状态码
        if (err.response.status === 401) {
          message.error('认证失败，请重新登录');
        } else if (err.response.status === 403) {
          message.error('权限不足，无法执行此操作');
        } else {
          message.error(`添加失败: ${err.response.data?.error || err.response.statusText}`);
        }
      } else if (err.request) {
        // 请求已发出但没有收到响应
        message.error('无法连接到服务器，请检查后端服务是否运行');
      } else {
        // 其他错误
        message.error(`添加插件失败: ${err.message}`);
      }
    }
  };

  const editPlugin = async (values: EditPluginFormValues) => {
    if (!editingPlugin) return;
    
    try {
      // 检查认证令牌
      const token = localStorage.getItem('authToken');
      if (!token) {
        message.error('认证令牌缺失，请重新登录');
        return;
      }
      
      // 构建更新数据，保持默认的模块路径和函数名
      const updateData: any = {
        description: values.description,
        enabled: values.enabled,
        schedule: values.schedule,
        parameters: values.parameters
      };
      
      // 保留原来的模块路径和函数名，除非它们存在
      if (editingPlugin.module_path) {
        updateData.module_path = editingPlugin.module_path;
      } else {
        updateData.module_path = `subscribe.scripts.${editingPlugin.name}`;
      }
      
      if (editingPlugin.function_name) {
        updateData.function_name = editingPlugin.function_name;
      } else {
        updateData.function_name = 'main';
      }
      
      const response = await axios.put(`http://localhost:5000/api/plugins/${editingPlugin.name}`, updateData);
      
      if (response.data.success) {
        message.success(response.data.message);
        setEditModalVisible(false);
        editForm.resetFields();
        // 刷新列表以确保数据一致性
        fetchPlugins();
      } else {
        message.error(response.data.error || '更新插件失败');
        // 操作失败后重新获取列表
        fetchPlugins();
      }
    } catch (err: any) {
      console.error('更新插件失败:', err);
      
      // 检查错误类型并给出更具体的错误信息
      if (err.response) {
        // 服务器响应了错误状态码
        if (err.response.status === 401) {
          message.error('认证失败，请重新登录');
        } else if (err.response.status === 403) {
          message.error('权限不足，无法执行此操作');
        } else {
          message.error(`更新失败: ${err.response.data?.error || err.response.statusText}`);
        }
      } else if (err.request) {
        // 请求已发出但没有收到响应
        message.error('无法连接到服务器，请检查后端服务是否运行');
      } else {
        // 其他错误
        message.error(`更新插件失败: ${err.message}`);
      }
      
      // 请求失败后重新获取列表
      fetchPlugins();
    }
  };

  const validatePluginConfig = async (pluginName: string, config: any) => {
    try {
      // 检查认证令牌
      const token = localStorage.getItem('authToken');
      if (!token) {
        console.error('认证令牌缺失');
        return { success: false, error: '认证令牌缺失，请重新登录' };
      }
      
      const response = await axios.post(`http://localhost:5000/api/plugins/${pluginName}/validate`, config);
      return response.data;
    } catch (error: any) {
      console.error('验证插件配置失败:', error);
      
      // 检查错误类型并给出更具体的错误信息
      if (error.response) {
        // 服务器响应了错误状态码
        if (error.response.status === 401) {
          return { success: false, error: '认证失败，请重新登录' };
        } else if (error.response.status === 403) {
          return { success: false, error: '权限不足，无法验证配置' };
        } else {
          return { success: false, error: `验证失败: ${error.response.data?.error || error.response.statusText}` };
        }
      } else if (error.request) {
        // 请求已发出但没有收到响应
        return { success: false, error: '无法连接到服务器，请检查后端服务是否运行' };
      } else {
        // 其他错误
        return { success: false, error: `验证插件配置失败: ${error.message}` };
      }
    }
  };

  const updatePluginConfig = async (pluginName: string, config: string) => {
    try {
      // 检查认证令牌
      const token = localStorage.getItem('authToken');
      if (!token) {
        message.error('认证令牌缺失，请重新登录');
        return false;
      }
      
      // 验证JSON格式
      let pluginConfig;
      try {
        pluginConfig = JSON.parse(config);
      } catch (e) {
        message.error('配置不是有效的JSON格式');
        return false;
      }
      
      // 首先验证插件配置
      const validation = await validatePluginConfig(pluginName, pluginConfig);
      if (!validation.success) {
        message.error(validation.message || validation.error || '插件配置验证失败');
        return false;
      }
      
      // 获取完整的插件配置
      const response = await axios.get('http://localhost:5000/api/config/plugin');
      if (response.data.success) {
        const fullConfig = response.data.data;
        
        // 更新特定插件的配置
        if (!fullConfig.plugins) {
          fullConfig.plugins = {};
        }
        fullConfig.plugins[pluginName] = pluginConfig;
        
        // 保存完整配置
        const saveResponse = await axios.put('http://localhost:5000/api/config/plugin', fullConfig);
        if (saveResponse.data.success) {
          message.success('插件配置已更新');
          setConfigModalVisible(false);
          fetchPlugins(); // 刷新列表以确保数据同步
          return true;
        } else {
          message.error(saveResponse.data.error || '更新插件配置失败');
          return false;
        }
      } else {
        message.error(response.data.error || '获取插件配置失败');
        return false;
      }
    } catch (err: any) {
      console.error('更新插件配置失败:', err);
      
      // 检查错误类型并给出更具体的错误信息
      if (err.response) {
        // 服务器响应了错误状态码
        if (err.response.status === 401) {
          message.error('认证失败，请重新登录');
        } else if (err.response.status === 403) {
          message.error('权限不足，无法执行此操作');
        } else {
          message.error(`更新配置失败: ${err.response.data?.error || err.response.statusText}`);
        }
      } else if (err.request) {
        // 请求已发出但没有收到响应
        message.error('无法连接到服务器，请检查后端服务是否运行');
      } else {
        // 其他错误
        message.error(`更新插件配置失败: ${err.message}`);
      }
      return false;
    }
  };

  const deletePlugin = async (pluginName: string) => {
    try {
      // 检查认证令牌
      const token = localStorage.getItem('authToken');
      if (!token) {
        message.error('认证令牌缺失，请重新登录');
        return;
      }
      
      const response = await axios.delete(`http://localhost:5000/api/plugins/${pluginName}/delete`);
      
      if (response.data.success) {
        message.success(response.data.message);
        // 操作成功后刷新插件列表
        fetchPlugins();
      } else {
        message.error(response.data.error || '删除插件失败');
      }
    } catch (error: any) {
      console.error('删除插件失败:', error);
      
      // 检查错误类型并给出更具体的错误信息
      if (error.response) {
        // 服务器响应了错误状态码
        if (error.response.status === 401) {
          message.error('认证失败，请重新登录');
        } else if (error.response.status === 403) {
          message.error('权限不足，无法执行此操作');
        } else {
          message.error(`删除失败: ${error.response.data?.error || error.response.statusText}`);
        }
      } else if (error.request) {
        // 请求已发出但没有收到响应
        message.error('无法连接到服务器，请检查后端服务是否运行');
      } else {
        // 其他错误
        message.error(`删除插件失败: ${error.message}`);
      }
    }
  };

  const togglePlugin = async (pluginName: string, enabled: boolean) => {
    try {
      // 显示加载状态
      message.loading({
        content: enabled ? '正在启用插件...' : '正在禁用插件...',
        duration: 0,
        key: 'toggle-plugin'
      });
      
      // 检查认证令牌
      const token = localStorage.getItem('authToken');
      if (!token) {
        message.error({
          content: '认证令牌缺失，请重新登录',
          key: 'toggle-plugin'
        });
        return;
      }
      
      const response = enabled 
        ? await axios.post(`http://localhost:5000/api/plugins/${pluginName}/enable`)
        : await axios.post(`http://localhost:5000/api/plugins/${pluginName}/disable`);
      
      if (response.data.success) {
        message.success({
          content: enabled ? '插件已启用' : '插件已禁用',
          key: 'toggle-plugin'
        });
        // 操作成功后刷新插件列表以确保状态同步
        fetchPlugins();
      } else {
        message.error({
          content: response.data.error || '操作失败',
          key: 'toggle-plugin'
        });
      }
    } catch (error: any) {
      console.error('操作插件失败:', error);
      
      // 检查错误类型并给出更具体的错误信息
      if (error.response) {
        // 服务器响应了错误状态码
        if (error.response.status === 401) {
          message.error({
            content: '认证失败，请重新登录',
            key: 'toggle-plugin'
          });
        } else if (error.response.status === 403) {
          message.error({
            content: '权限不足，无法执行此操作',
            key: 'toggle-plugin'
          });
        } else {
          message.error({
            content: `操作失败: ${error.response.data?.error || error.response.statusText}`,
            key: 'toggle-plugin'
          });
        }
      } else if (error.request) {
        // 请求已发出但没有收到响应
        message.error({
          content: '无法连接到服务器，请检查后端服务是否运行',
          key: 'toggle-plugin'
        });
      } else {
        // 其他错误
        message.error({
          content: `操作插件失败: ${error.message}`,
          key: 'toggle-plugin'
        });
      }
    }
  };

  const runPlugin = async (pluginName: string) => {
    try {
      // 显示加载状态
      message.loading({
        content: '正在启动插件执行...',
        duration: 0,
        key: 'run-plugin'
      });
      
      // 检查认证令牌
      const token = localStorage.getItem('authToken');
      if (!token) {
        message.error({
          content: '认证令牌缺失，请重新登录',
          key: 'run-plugin'
        });
        return;
      }
      
      const response = await axios.post(`http://localhost:5000/api/plugins/${pluginName}/run`);
      if (response.data.success) {
        message.success({
          content: '插件已启动执行',
          key: 'run-plugin'
        });
        // 3秒后刷新插件列表以获取最新状态
        setTimeout(() => {
          fetchPlugins();
        }, 3000);
      } else {
        message.error({
          content: response.data.error || '执行失败',
          key: 'run-plugin'
        });
      }
    } catch (error: any) {
      console.error('执行插件失败:', error);
      
      // 检查错误类型并给出更具体的错误信息
      if (error.response) {
        // 服务器响应了错误状态码
        if (error.response.status === 401) {
          message.error({
            content: '认证失败，请重新登录',
            key: 'run-plugin'
          });
        } else if (error.response.status === 403) {
          message.error({
            content: '权限不足，无法执行此操作',
            key: 'run-plugin'
          });
        } else {
          message.error({
            content: `执行失败: ${error.response.data?.error || error.response.statusText}`,
            key: 'run-plugin'
          });
        }
      } else if (error.request) {
        // 请求已发出但没有收到响应
        message.error({
          content: '无法连接到服务器，请检查后端服务是否运行',
          key: 'run-plugin'
        });
      } else {
        // 其他错误
        message.error({
          content: `执行插件失败: ${error.message}`,
          key: 'run-plugin'
        });
      }
    }
  };

  const showEditModal = (plugin: Plugin) => {
    setEditingPlugin(plugin);
    editForm.setFieldsValue({
      description: plugin.description,
      enabled: plugin.enabled,
      schedule: plugin.schedule,
      parameters: plugin.parameters || {}
    });
    setEditModalVisible(true);
  };

  const showConfigModal = async (plugin: Plugin) => {
    const configStr = await fetchPluginConfig(plugin.name);
    setEditingPlugin(plugin);
    setEditingConfig(configStr || JSON.stringify(plugin, null, 2));
    setConfigModalVisible(true);
    setConfigTabActiveKey('json');
  };

  // 检查是否已认证，未认证时显示提示
  if (!isAuthenticated) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <h2>请先登录以访问插件管理功能</h2>
      </div>
    );
  }

  const showModal = () => {
    setModalVisible(true);
  };

  const handleCancel = () => {
    setModalVisible(false);
    form.resetFields();
  };

  const handleEditCancel = () => {
    setEditModalVisible(false);
    setEditingPlugin(null);
    editForm.resetFields();
  };

  const handleConfigCancel = () => {
    setConfigModalVisible(false);
    setEditingPlugin(null);
    setEditingConfig('');
  };

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      await addPlugin(values);
    } catch (error) {
      console.log('表单验证失败:', error);
    }
  };

  const handleEditOk = async () => {
    try {
      const values = await editForm.validateFields();
      await editPlugin(values);
    } catch (error) {
      console.log('编辑表单验证失败:', error);
    }
  };

  const handleConfigOk = async () => {
    if (!editingPlugin) return;
    
    const success = await updatePluginConfig(editingPlugin.name, editingConfig);
    if (success) {
      setConfigModalVisible(false);
      setEditingPlugin(null);
      setEditingConfig('');
    }
  };

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
      width: '25%',
    },
    {
      title: '状态',
      key: 'status',
      width: '10%',
      render: (_text: any, record: Plugin) => (
        <Tag color={record.status === 'running' ? 'green' : record.status === 'error' ? 'red' : 'default'} style={{ borderRadius: 6, fontWeight: 500 }}>
          {record.status === 'running' ? '运行中' : record.status === 'error' ? '错误' : '空闲'}
        </Tag>
      ),
    },
    {
      title: '启用',
      key: 'enabled',
      width: '10%',
      render: (_text: any, record: Plugin) => (
        <Switch
          checked={record.enabled}
          onChange={(checked) => togglePlugin(record.name, checked)}
          style={{ minWidth: 44 }}
        />
      ),
    },
    {
      title: '定时配置',
      dataIndex: 'schedule',
      key: 'schedule',
      width: '15%',
    },
    {
      title: '操作',
      key: 'action',
      width: '25%',
      render: (_text: any, record: Plugin) => (
        <Space size="small">
          <Button 
            type="primary" 
            icon={<PlayCircleOutlined />} 
            onClick={() => runPlugin(record.name)}
            disabled={!record.enabled}
            size="small"
            style={{ borderRadius: 6 }}
          >
            运行
          </Button>
          <Button 
            icon={<ReloadOutlined />} 
            onClick={fetchPlugins}
            size="small"
            style={{ borderRadius: 6 }}
          >
            刷新
          </Button>
          <Button 
            type="default"
            icon={<EditOutlined />}
            onClick={() => showEditModal(record)}
            size="small"
            style={{ borderRadius: 6 }}
          >
            编辑
          </Button>
          <Button 
            type="default"
            icon={<FileTextOutlined />}
            onClick={() => showConfigModal(record)}
            size="small"
            style={{ borderRadius: 6 }}
          >
            配置
          </Button>
          <Popconfirm
            title="确认删除"
            description={`确定要删除插件 "${record.name}" 吗？`}
            onConfirm={() => deletePlugin(record.name)}
            okText="确定"
            cancelText="取消"
          >
            <Button 
              danger
              icon={<DeleteOutlined />}
              size="small"
              style={{ borderRadius: 6 }}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card className="glass-card" title="插件管理" style={{ marginBottom: 24, borderRadius: 20, border: '1px solid rgba(255, 255, 255, 0.4)' }}>
        <p style={{ color: 'var(--text-secondary)' }}>管理插件的启用状态、执行和配置</p>
      </Card>
      <Card className="glass-card" style={{ marginBottom: 24, borderRadius: 20, border: '1px solid rgba(255, 255, 255, 0.4)' }}>
        <Button 
          type="primary" 
          icon={<PlusOutlined />} 
          onClick={showModal}
          style={{ borderRadius: 8, fontWeight: 500, height: 40 }}
        >
          添加插件
        </Button>
      </Card>
      <Card className="glass-card" style={{ borderRadius: 20, border: '1px solid rgba(255, 255, 255, 0.4)' }}>
        <Table 
          columns={columns} 
          dataSource={plugins} 
          rowKey="name"
          loading={loading}
          size="middle"
        />
      </Card>
      
      <Modal
        title="添加插件"
        open={modalVisible}
        onOk={handleOk}
        onCancel={handleCancel}
        okText="添加"
        cancelText="取消"
        className="glass-card"
        style={{ borderRadius: 20 }}
        bodyStyle={{ padding: 24 }}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="插件名称"
            rules={[{ required: true, message: '请输入插件名称' }]}
          >
            <Input placeholder="例如：my_custom_plugin" />
          </Form.Item>
          <Form.Item
            name="description"
            label="描述"
            rules={[{ required: true, message: '请输入插件描述' }]}
          >
            <Input placeholder="插件的描述信息" />
          </Form.Item>

          <Form.Item
            name="enabled"
            label="默认启用"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
          <Form.Item
            name="schedule"
            label="定时任务 (Cron表达式)"
          >
            <Input placeholder="例如：0 2 * * * (每天凌晨2点执行)" />
          </Form.Item>
          <Form.Item
            name="upload"
            label="上传插件脚本"
          >
            <Upload
              accept=".py"
              maxCount={1}
              beforeUpload={() => {
                // 不自动上传，只是保存文件引用
                return false;
              }}
              onChange={(info) => {
                if (info.fileList.length > 0) {
                  // 当选择了文件，更新表单中的文件信息
                  form.setFieldsValue({ upload: info.fileList });
                }
              }}
            >
              <Button icon={<UploadOutlined />}>点击上传Python脚本</Button>
            </Upload>
            <div style={{ marginTop: 8 }}>
              <small>提示：您可以选择上传Python脚本文件(.py)，或者只添加配置信息</small>
            </div>
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={`编辑插件 - ${editingPlugin?.name}`}
        open={editModalVisible}
        onOk={handleEditOk}
        onCancel={handleEditCancel}
        okText="更新"
        cancelText="取消"
        className="glass-card"
        style={{ borderRadius: 20 }}
        bodyStyle={{ padding: 24 }}
      >
        <Form form={editForm} layout="vertical">
          <Form.Item
            name="description"
            label="描述"
            rules={[{ required: true, message: '请输入插件描述' }]}
          >
            <Input placeholder="插件的描述信息" />
          </Form.Item>
          <Form.Item
            name="enabled"
            label="启用状态"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
          <Form.Item
            name="schedule"
            label="定时任务 (Cron表达式)"
          >
            <Input placeholder="例如：0 2 * * * (每天凌晨2点执行)" />
          </Form.Item>
          <Form.Item
            name="parameters"
            label="参数配置 (JSON格式)"
          >
            <Input.TextArea 
              rows={4}
              placeholder='例如：{"param1": "value1", "param2": "value2"}' 
            />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={`编辑插件配置 - ${editingPlugin?.name}`}
        open={configModalVisible}
        onOk={handleConfigOk}
        onCancel={handleConfigCancel}
        okText="保存"
        cancelText="取消"
        width={850}
        className="glass-card"
        style={{ borderRadius: 20 }}
        bodyStyle={{ padding: 24 }}
        footer={[
          <Button key="back" onClick={handleConfigCancel} style={{ borderRadius: 6 }}>
            取消
          </Button>,
          <Button 
            key="validate" 
            onClick={() => {
              try {
                JSON.parse(editingConfig);
                message.success('配置格式验证通过');
              } catch (e) {
                message.error('配置格式错误，请检查JSON格式');
              }
            }}
            style={{ borderRadius: 6 }}
          >
            验证格式
          </Button>,
          <Button key="submit" type="primary" onClick={handleConfigOk} style={{ borderRadius: 6 }}>
            保存
          </Button>,
        ]}
      >
        <Tabs 
          activeKey={configTabActiveKey} 
          onChange={setConfigTabActiveKey}
          items={[
            {
              key: 'json',
              label: 'JSON配置',
              children: (
                <>
                  <Alert
                    message="配置说明"
                    description="在此编辑插件的完整配置，支持JSON格式。修改后请先验证格式再保存。"
                    type="info"
                    showIcon
                    style={{ marginBottom: 16 }}
                  />
                  <Form layout="vertical">
                    <Form.Item
                      label="插件配置 (JSON格式)"
                    >
                      <Input.TextArea 
                        rows={15}
                        value={editingConfig}
                        onChange={(e) => setEditingConfig(e.target.value)}
                        placeholder="在此处编辑插件的完整配置JSON"
                      />
                    </Form.Item>
                  </Form>
                </>
              ),
            },
            {
              key: 'help',
              label: '帮助',
              children: (
                <div>
                  <h4>插件配置结构说明</h4>
                  <pre style={{ backgroundColor: '#f5f5f5', padding: '10px', borderRadius: '4px' }}>
{`{
  "name": "插件名称",
  "description": "插件描述",
  "enabled": true/false,
  "cron_schedule": "定时任务表达式",
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  },
  "module_path": "模块路径",
  "function_name": "函数名"
}`}
                  </pre>
                  <p><strong>示例：</strong></p>
                  <pre style={{ backgroundColor: '#f5f5f5', padding: '10px', borderRadius: '4px' }}>
{`{
  "name": "example_plugin",
  "description": "示例插件",
  "enabled": true,
  "cron_schedule": "0 2 * * *",
  "parameters": {
    "api_key": "your_api_key",
    "timeout": 30
  },
  "module_path": "subscribe.scripts.example_plugin",
  "function_name": "main"
}`}
                  </pre>
                </div>
              ),
            }
          ]}
        />
      </Modal>
    </div>
  );
};

export default PluginManager;