import { Image as ExpoImage, type ImageProps } from 'expo-image';
import { cssInterop } from 'nativewind';
import type { ComponentType } from 'react';

cssInterop(ExpoImage, { className: 'style' });

export const Image = ExpoImage as ComponentType<
  ImageProps & { className?: string }
>;
