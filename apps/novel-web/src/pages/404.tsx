import { Link } from '@umijs/max';
import React from 'react';
import StateCard from '@/components/StateCard';

export default function NotFoundPage() {
  return (
    <div className="not-found">
      <p className="not-found-code">404</p>
      <StateCard
        title="这一页不在书架上"
        hint="地址不存在，或内容已被移除。"
        action={
          <Link to="/" className="btn-primary">
            回书架
          </Link>
        }
      />
    </div>
  );
}
