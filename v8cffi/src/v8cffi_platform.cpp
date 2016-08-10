#include "v8cffi_platform.h"

using namespace v8cffi_platform;


/*
 * This can only be initialized once per process,
 * it's enforced by V8, not here.
 * */
Platform::Platform(
  const std::string &natives_blob,
  const std::string &snapshot_blob)
{
#ifdef V8_I18N_SUPPORT
  v8::V8::InitializeICU();  // todo: check if true
#endif
#ifdef V8_USE_EXTERNAL_STARTUP_DATA
  // StartupData does not copy the string,
  // so we keep it alive
  m_natives_blob = natives_blob;
  m_snapshot_blob = snapshot_blob;

  m_natives.data = m_natives_blob.c_str();
  m_natives.raw_size = m_natives_blob.length();
  m_snapshot.data = m_snapshot_blob.c_str();
  m_snapshot.raw_size = m_snapshot_blob.length();

  v8::V8::SetNativesDataBlob(&m_natives);
  v8::V8::SetSnapshotDataBlob(&m_snapshot);
#endif
  m_platform = v8::platform::CreateDefaultPlatform();
  v8::V8::InitializePlatform(m_platform);  // todo: check if true
  v8::V8::Initialize();  // todo: check if true
}


Platform::~Platform()
{
  if (!m_platform)
    return;

  v8::V8::Dispose();
  v8::V8::ShutdownPlatform();

  delete m_platform;
  m_platform = nullptr;
}
