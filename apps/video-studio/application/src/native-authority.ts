import type { NativeReceipt } from "./domain";

const verifiedReceipt = Symbol("video-studio/verified-native-receipt");

export type VerifiedNativeReceipt = NativeReceipt & {
  readonly [verifiedReceipt]: true;
};

export const markVerifiedNativeReceipt = (receipt: NativeReceipt): VerifiedNativeReceipt => {
  const copy = { ...receipt } as VerifiedNativeReceipt;
  Object.defineProperty(copy, verifiedReceipt, { value: true, enumerable: false });
  return copy;
};

export const isVerifiedNativeReceipt = (receipt: NativeReceipt): receipt is VerifiedNativeReceipt =>
  (receipt as Partial<VerifiedNativeReceipt>)[verifiedReceipt] === true;
