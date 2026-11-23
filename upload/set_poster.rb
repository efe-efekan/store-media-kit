# Changes the poster (still) frame of already uploaded previews, without re-uploading.
#   bundle exec ruby <kit>/upload/set_poster.rb <project> 00:00:01:15
require_relative "asc"

project, poster = ARGV
abort("usage: set_poster.rb <project> HH:MM:SS:FF") unless project && poster =~ /\A\d\d:\d\d:\d\d:\d\d\z/
cfg = ASC.config(project)
type = (cfg["preview"] || {})["type"] || Spaceship::ConnectAPI::AppPreviewSet::PreviewType::IPHONE_67
ASC.login
_, version = ASC.edit_version(cfg)
version.get_app_store_version_localizations.sort_by(&:locale).each do |loc|
  set = loc.get_app_preview_sets.find { |s| s.preview_type == type } or next
  (set.app_previews || []).each do |p|
    before = p.preview_frame_time_code
    p.update(attributes: { previewFrameTimeCode: poster })
    puts "#{loc.locale.ljust(7)} #{before} -> #{poster}"
  end
end
