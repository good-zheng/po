import { request } from '@umijs/max';
import type { Result } from '@po/types';

/** 图片业务子目录白名单（对应后端 FileController.ALLOWED_DIRS） */
export type UploadDir = 'common' | 'dishes' | 'steps';

/**
 * 上传图片到后端 /api/files/upload（落腾讯云 COS），返回桶公网 URL。
 * file 字段名与 dir 参数须与后端 FileController 保持一致。
 */
export async function uploadImage(
  file: File,
  dir: UploadDir,
  options?: Record<string, unknown>,
) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('dir', dir);
  return request<Result<string>>('/api/files/upload', {
    method: 'POST',
    data: formData,
    ...(options || {}),
  });
}
