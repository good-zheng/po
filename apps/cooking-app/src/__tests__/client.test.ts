import type { Result } from '@po/types';
import type { AxiosResponse } from 'axios';

import { ApiError, resolveAssetUrl, unwrap } from '@/lib/api/client';

function response<T>(data: Result<T>): AxiosResponse<Result<T>> {
  return {
    config: { headers: {} },
    data,
    headers: {},
    status: 200,
    statusText: 'OK',
  } as AxiosResponse<Result<T>>;
}

describe('unwrap', () => {
  it('returns data from a successful API response', () => {
    expect(
      unwrap(
        response({
          code: 200,
          data: { id: 1 },
          message: '成功',
          success: true,
        }),
      ),
    ).toEqual({ id: 1 });
  });

  it('throws an ApiError for a rejected API response', () => {
    expect(() =>
      unwrap(
        response({
          code: 400,
          data: null,
          message: '参数无效',
          success: false,
        }),
      ),
    ).toThrow(ApiError);
  });
});

describe('resolveAssetUrl', () => {
  it('returns undefined without a path', () => {
    expect(resolveAssetUrl()).toBeUndefined();
    expect(resolveAssetUrl(null)).toBeUndefined();
    expect(resolveAssetUrl('')).toBeUndefined();
  });

  it('keeps absolute URLs untouched', () => {
    expect(resolveAssetUrl('https://cdn.po.dev/avatar.jpg')).toBe(
      'https://cdn.po.dev/avatar.jpg',
    );
    expect(resolveAssetUrl('http://192.168.1.10:8080/avatar.jpg')).toBe(
      'http://192.168.1.10:8080/avatar.jpg',
    );
  });

  it('resolves backend-relative paths against the API root', () => {
    expect(resolveAssetUrl('/api/avatars/x.jpg')).toMatch(
      /\/api\/avatars\/x\.jpg$/,
    );
    expect(resolveAssetUrl('api/avatars/x.jpg')).toBe(
      resolveAssetUrl('/api/avatars/x.jpg'),
    );
  });
});
