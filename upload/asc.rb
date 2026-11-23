# Shared App Store Connect login for the upload scripts (Spaceship, the library inside fastlane).
#
# Credentials never live in the repo:
#   FASTLANE_USER       Apple ID e-mail (uses fastlane's saved session / keychain password)
#   FASTLANE_TEAM_ID    App Store Connect team id (optional when you have one team)
# Run from the app folder that has fastlane in its Gemfile:
#   LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 bundle exec ruby <kit>/upload/<script>.rb <project>
require "json"
require "spaceship"

module ASC
  module_function

  def config(project)
    path = File.directory?(project) ? File.join(project, "media.json") : project
    abort("missing #{path}") unless File.exist?(path)
    cfg = JSON.parse(File.read(path))
    cfg["_dir"] = File.dirname(File.expand_path(path))
    cfg
  end

  def login
    user = ENV["FASTLANE_USER"] or abort("set FASTLANE_USER to your Apple ID e-mail")
    opts = { use_portal: false, use_tunes: true }
    opts[:tunes_team_id] = ENV["FASTLANE_TEAM_ID"] if ENV["FASTLANE_TEAM_ID"]
    Spaceship::ConnectAPI.login(user, **opts)
  end

  # The editable ("Prepare for Submission") iOS version of the app in media.json.
  def edit_version(cfg)
    bundle = cfg.dig("app", "bundle_id") or abort("media.json: app.bundle_id is missing")
    app = Spaceship::ConnectAPI::App.find(bundle) or abort("no app with bundle id #{bundle}")
    v = app.get_edit_app_store_version(platform: Spaceship::ConnectAPI::Platform::IOS)
    abort("#{bundle}: no editable version (create one in App Store Connect)") unless v
    [app, v]
  end
end
