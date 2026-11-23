# Read-only: screenshot and preview counts (and processing state) per store locale.
#   bundle exec ruby <kit>/upload/verify_media.rb <project>
require_relative "asc"

cfg = ASC.config(ARGV[0] || abort("usage: verify_media.rb <project>"))
ASC.login
_, version = ASC.edit_version(cfg)
version.get_app_store_version_localizations.sort_by(&:locale).each do |l|
  shots = l.get_app_screenshot_sets.map { |s| "#{s.screenshot_display_type}:#{(s.app_screenshots || []).size}" }.join(",")
  prev = l.get_app_preview_sets.map do |s|
    "#{s.preview_type}:" + (s.app_previews || []).map { |p| p.asset_delivery_state&.dig("state") || "?" }.join("/")
  end.join(",")
  puts "#{l.locale.ljust(8)} shots[#{shots}] previews[#{prev}]"
end
