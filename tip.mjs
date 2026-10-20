/**
 * Optional support button for the FREE original One Cursor stablecoin screener.
 * User explicitly initiates only a LOCAL clipboard copy of the public merchant
 * destination; NEVER reads a wallet, constructs/sends a transaction, navigates to
 * dApps, or requests permission/signatures.
 *
 * PayTo source: original one-human-owner VM5 firstparty GET402 at
 * https://vm5-openapi-x402.onrender.com/v1/csv-report
 * (x402Version2 accepts[0] payTo, eip155:8453, exact native Circle Base USDC)
 * independently checked 2026-10-21. Address is also the existing VM5 original
 * OpenTask payout entry and original one-beneficial-owner 64-confirmation watch.
 */
export const TIP_DETAILS = Object.freeze({
  network: "Base mainnet",
  chainId: 8453,
  asset: "Native Circle USDC",
  assetAddress: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
  publicPayTo: "0x6b01efA0705E91a7aca54271510bf9e594717f34",
  voluntaryExampleUsdc: "1",
  paymentCreatesOrder: false,
  tipsAreVoluntary: true,
  browserAutoTransfers: false
});
export function validatePublicTipDetails(d = TIP_DETAILS) {
  if (d.chainId !== 8453 || d.network !== "Base mainnet" ||
      String(d.assetAddress).toLowerCase() !== "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913" ||
      String(d.publicPayTo).toLowerCase() !== "0x6b01efa0705e91a7aca54271510bf9e594717f34" ||
      d.paymentCreatesOrder !== false || d.browserAutoTransfers !== false) {
    throw new TypeError("Refuse to suggest an unverified payment destination");
  }
  return d.publicPayTo;
}
/** Return boolean only: no address exposure in error logs, UI or network. */
export async function copyPublicReceiver(clipboard, details = TIP_DETAILS) {
  const address = validatePublicTipDetails(details);
  if (!clipboard || typeof clipboard.writeText !== "function") return false;
  try {
    await clipboard.writeText(address);
    return true;
  } catch {
    return false;
  }
}
if (typeof document !== "undefined") {
  const button = document.getElementById("copy-public-tip-recipient");
  const status = document.getElementById("tip-copy-status");
  if (button && status) {
    button.addEventListener("click", async () => {
      status.textContent = "Attempting to copy the public address only…";
      const ok = await copyPublicReceiver(
        typeof navigator !== "undefined" ? navigator.clipboard : null
      );
      status.textContent = ok
        ? "Public address copied. Before any voluntary payment, independently verify Base mainnet (8453), native Circle USDC token and the recipient. We never receive transaction data here."
        : "Clipboard permission unavailable. You can manually select and copy the public address. This page never requests a wallet signature.";
    });
  }
}
