import { Button, Input, Text, View } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { useState } from 'react';

import { useAuth } from '@/lib/auth/auth-context';
import { consumeReturnTo, isTabPath } from '@/lib/auth/return-path';
import './index.scss';

type Tab = 'wechat' | 'login' | 'register';

/** 登录成功回来路：tab 页只能 switchTab，普通页用 redirectTo 免得返回又落回登录页 */
function redirectAfterLogin() {
  const returnTo = consumeReturnTo();
  if (returnTo) {
    const path = returnTo.split('?')[0];
    if (isTabPath(path)) {
      Taro.switchTab({ url: path });
    } else {
      Taro.redirectTo({ url: returnTo });
    }
    return;
  }
  Taro.switchTab({ url: '/pages/session/index' });
}

export default function LoginPage() {
  const { signInWithOpenId, signInWithPassword, register } = useAuth();
  const [tab, setTab] = useState<Tab>('wechat');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '' as 'error' | 'info' | '', text: '' });

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [regUsername, setRegUsername] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regNickname, setRegNickname] = useState('');

  const showError = (text: string) => setMessage({ type: 'error', text });
  const showInfo = (text: string) => setMessage({ type: 'info', text });
  const clearMessage = () => setMessage({ type: '', text: '' });

  const handleOpenIdLogin = async () => {
    setLoading(true);
    clearMessage();
    try {
      const loginRes = await Taro.login();
      if (!loginRes.code) {
        showError('微信登录失败，请重试');
        return;
      }
      const result = await signInWithOpenId(loginRes.code);
      if (result.approved) {
        redirectAfterLogin();
      } else if (result.approvalStatus === 'pending') {
        showInfo('注册成功，请等待管理员审批后再登录');
      } else if (result.approvalStatus === 'rejected') {
        showError('注册申请已被拒绝，请联系管理员');
      }
    } catch (err: any) {
      showError(err.message || '登录失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordLogin = async () => {
    if (!username.trim() || !password.trim()) {
      showError('请输入用户名和密码');
      return;
    }
    setLoading(true);
    clearMessage();
    try {
      const result = await signInWithPassword(username.trim(), password);
      if (result.approved) {
        redirectAfterLogin();
      } else if (result.approvalStatus === 'pending') {
        showInfo('账号正在等待管理员审批');
      } else if (result.approvalStatus === 'rejected') {
        showError('注册申请已被拒绝，请联系管理员');
      }
    } catch (err: any) {
      showError(err.message || '登录失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async () => {
    if (!regUsername.trim() || !regPassword.trim()) {
      showError('请输入用户名和密码');
      return;
    }
    if (regPassword.length < 6) {
      showError('密码至少 6 位');
      return;
    }
    setLoading(true);
    clearMessage();
    try {
      await register(regUsername.trim(), regPassword, regNickname.trim() || undefined);
      showInfo('注册成功，请等待管理员审批后再登录');
      setRegUsername('');
      setRegPassword('');
      setRegNickname('');
    } catch (err: any) {
      showError(err.message || '注册失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const switchTab = (t: Tab) => {
    setTab(t);
    clearMessage();
  };

  return (
    <View className='login'>
      <View className='login-header'>
        <Text className='login-title'>言外</Text>
        <Text className='login-subtitle'>听懂他没说出口的那句</Text>
      </View>

      <View className='tab-bar'>
        <View
          className={`tab-item ${tab === 'wechat' ? 'active' : ''}`}
          onClick={() => switchTab('wechat')}
        >
          <Text>微信登录</Text>
        </View>
        <View
          className={`tab-item ${tab === 'login' ? 'active' : ''}`}
          onClick={() => switchTab('login')}
        >
          <Text>密码登录</Text>
        </View>
        <View
          className={`tab-item ${tab === 'register' ? 'active' : ''}`}
          onClick={() => switchTab('register')}
        >
          <Text>注册</Text>
        </View>
      </View>

      {message.text ? (
        <View className={`login-message ${message.type}`}>
          <Text className='message-text'>{message.text}</Text>
        </View>
      ) : null}

      {tab === 'wechat' && (
        <View className='tab-content'>
          <View className='login-icon'>{'\u{1F442}'}</View>
          <Text className='login-desc'>使用微信身份快速登录，录音与对话记录跟着账号走</Text>
          <Button className='action-btn wechat-btn' onClick={() => void handleOpenIdLogin()} disabled={loading}>
            {loading ? '登录中...' : '微信一键登录'}
          </Button>
        </View>
      )}

      {tab === 'login' && (
        <View className='tab-content'>
          <Input
            className='input'
            placeholder='用户名'
            value={username}
            onInput={(e) => setUsername(e.detail.value)}
          />
          <Input
            className='input'
            placeholder='密码'
            password
            value={password}
            onInput={(e) => setPassword(e.detail.value)}
          />
          <Button className='action-btn login-btn' onClick={() => void handlePasswordLogin()} disabled={loading}>
            {loading ? '登录中...' : '登录'}
          </Button>
        </View>
      )}

      {tab === 'register' && (
        <View className='tab-content'>
          <Input
            className='input'
            placeholder='用户名（3-32 位）'
            value={regUsername}
            onInput={(e) => setRegUsername(e.detail.value)}
          />
          <Input
            className='input'
            placeholder='密码（至少 6 位）'
            password
            value={regPassword}
            onInput={(e) => setRegPassword(e.detail.value)}
          />
          <Input
            className='input'
            placeholder='昵称（选填）'
            value={regNickname}
            onInput={(e) => setRegNickname(e.detail.value)}
          />
          <Button className='action-btn register-btn' onClick={() => void handleRegister()} disabled={loading}>
            {loading ? '注册中...' : '提交注册'}
          </Button>
          <Text className='register-hint'>注册后需等待管理员审批</Text>
        </View>
      )}

      <View className='login-footer'>
        <Text className='footer-text'>登录即表示同意用户协议和隐私政策</Text>
      </View>
    </View>
  );
}
