# Uploads the App Preview video(s) to the editable version (fastlane deliver cannot).
#
#   bundle exec ruby <kit>/upload/upload_previews.rb <project> [video-locale]
#
# media.json "preview": { "store_locales": ["en-US", ...], "poster": "00:00:01:15",
#                         "file": "video/out/en.mp4", "type": "IPHONE_67" }
# Existing previews of that type in those locales are replaced. Locales without a preview
# show the primary language's preview on the store, so one English video is often enough.
require_relative "asc"

project = ARGV[0] or abort("usage: upload_previews.rb <project> [video-locale]")
cfg = ASC.config(project)
pv = cfg["preview"] || {}
locale = ARGV[1] || "en"
file = File.join(cfg["_dir"], pv["file"] || "video/out/#{locale}.mp4")
abort("missing #{file} (render it: cd video && npm run render -- #{locale})") unless File.exist?(file)
targets = pv["store_locales"] || ["en-US"]
poster = pv["poster"] || "00:00:01:15"
type = pv["type"] || Spaceship::ConnectAPI::AppPreviewSet::PreviewType::IPHONE_67

ASC.login
_, version = ASC.edit_version(cfg)
locs = version.get_app_store_version_localizations.map { |l| [l.locale, l] }.to_h
ok = 0
targets.each do |store_locale|
  loc = locs[store_locale] or (puts("skip #{store_locale}: not a localization of this version"); next)
  set = loc.get_app_preview_sets.find { |s| s.preview_type == type }
  set ||= loc.create_app_preview_set(attributes: { previewType: type })
  (set.app_previews || []).each(&:delete!)
  set.upload_preview(path: file, wait_for_processing: false, frame_time_code: poster)
  ok += 1
  puts "uploaded #{store_locale} <- #{File.basename(file)} (poster #{poster})"
end
puts "done #{ok}/#{targets.size} - Apple processes the video for a few minutes; run verify_media.rb"
