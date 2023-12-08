
autoload -Uz compinit promptinit colors
compinit
promptinit
colors


####################
# Autocompletition #
####################

# Disable autocorrect dialog
unsetopt correct
unsetopt correct_all

# Use bash completions
autoload -U +X bashcompinit && bashcompinit

setopt completealiases
setopt extendedglob
unset menucomplete
unsetopt automenu
setopt GLOB_COMPLETE


##################
# Prompt styling #
##################

# VCS info
autoload -Uz vcs_info
zstyle ':vcs_info:*' enable ALL
zstyle ':vcs_info:*' get-revision true
zstyle ':vcs_info:*' check-for-changes true
zstyle ':vcs_info:git*:*' formats "%{$fg[blue]%}[%s:%b:%.6i]%{$reset_color%}%{$fg[green]%} %u %c%{$reset_color%}"
zstyle ':vcs_info:git*:*' actionformats "%{$fg[blue]%}[%s:%b:%.6i]%{$reset_color%}%{$fg[green]%} %u %c %a%{$reset_color%}"
precmd() { vcs_info }

# Nicer virtualenv info
export VIRTUAL_ENV_DISABLE_PROMPT=yes
virtenv_indicator() {
  if [[ -z $VIRTUAL_ENV ]] then
    psvar[1]=''
  else
    psvar[1]=${VIRTUAL_ENV##*/}
  fi
}
add-zsh-hook precmd virtenv_indicator

_check_infoline () {
  if [[ -n "$vcs_info_msg_0_" ]]; then
    psvar[2]=1
  elif [[ -n "$VIRTUAL_ENV" ]]; then
    psvar[2]=1
  elif [[ -n `jobs` ]]; then
    psvar[2]=1
  else
    psvar[2]=''
  fi
}
add-zsh-hook precmd _check_infoline

# Set user and computer colors
setopt prompt_subst
system_color="green"
user_color="green"

prompt='${vcs_info_msg_0_}%{$fg[yellow]%}%(1V.(%1v) .)%{$fg[magenta]%}%(1j.[%j] .)%{$fg[red]%}%(?..!%? )%(2V.
.)%{$fg[cyan]%}[20%D %*] %{$fg[$user_color]%}%n%{$fg[$system_color]%}@%M%{$fg[cyan]%}:%~
%{$reset_color%}%(!.#.$) '


###########
# History #
###########
autoload history-search-end
zle -N history-beginning-search-backward-end history-search-end
zle -N history-beginning-search-forward-end history-search-end
zle -N up-line-or-beginning-search
zle -N down-line-or-beginning-search
setopt hist_ignore_all_dups
setopt share_history
setopt hist_verify
export HISTSIZE=5000
export SAVEHIST=$HISTSIZE
export HISTFILE="$HOME/.zsh_history"


################
# Key bindings #
################

# Enable vi -mode
bindkey -v
bindkey -M vicmd 'k' history-beginning-search-backward-end
bindkey -M vicmd 'j' history-beginning-search-forward-end

# Emacs key bindings
bindkey "^A" beginning-of-line
bindkey "^E" end-of-line
bindkey "^K" kill-line
bindkey "^L" clear-screen
bindkey "^R" history-incremental-search-backward
bindkey "^U" backward-kill-line
bindkey "^W" backward-kill-word
bindkey "^Y" yank

bindkey '^[[1;5C' forward-word
bindkey '^[[1;5D' backward-word
bindkey '^?' backward-delete-char

[[ -n "${terminfo[khome]}" ]] && bindkey "${terminfo[khome]}" beginning-of-line
[[ -n "${terminfo[kend]}" ]] && bindkey "${terminfo[kend]}" end-of-line


#############################
# Environment configuration #
#############################

export LANG="en_US.UTF-8"
export LANGUAGE="en_US:en"
export LC_CTYPE="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"
export EDITOR=vim
if [ -d "$HOME/.local/bin" ]; then
  export PATH="$HOME/.local/bin:$PATH"
fi


#######################
# Aliases and helpers #
#######################

# Suffix aliases
alias -s txt="vim"
alias -s rst="vim"
alias -s md="vim"
alias -s conf="vim"
alias -s sls="vim"
alias -s yml="vim"

# enable color support for ls and grep
if [ -x /usr/bin/dircolors ]; then
  if [ -f ~/.dircolors ]; then
    eval `dircolors -b ~/.dircolors`
  else
    eval `dircolors -b`
  fi

  alias ls='ls --time-style=long-iso --color=auto'

  alias grep='grep --color=auto'
  alias fgrep='fgrep --color=auto'
  alias egrep='egrep --color=auto'
else
  alias ls='ls --time-style=long-iso'
fi

if [ -f "$HOME/.aliasses.sh" ]; then
  . $HOME/.aliasses.sh
fi
if [ -f "$HOME/.local/aliasses.sh" ]; then
  . $HOME/.local/aliasses.sh
fi


###################
# Shell functions #
###################

# Handy all-in-one date format helper
dt() {
  if [ -n "$*" ]; then
    date +%F\ %T\ %Z\ -\ w%V\ %A --date="$*"
  else
    date +%F\ %T\ %Z\ -\ w%V\ %A
  fi
}

# List processes listening or connecting to given port
netgrep() {
  lsof -i :$1
}

# grep which process is listening on given tcp-port
tcpgrep() {
  lsof -i tcp:$1
}

# Like pgrep but show process with ps
psgrep () {
  pgrep $1 | xargs ps u
}
compdef check_dns=dig


#######################################
# Activate Python virtual environment #
#######################################

if [[ -d ~/.venv ]]; then
  . ~/.venv/bin/activate
fi


##############
# Finalizing #
##############

# You can add your custon settings in ~/.zsh/local.zsh
if [[ -r ~/.zsh/local.zsh ]]; then
  . ~/.zsh/local.zsh
fi

# Display motd
if [[ -e /etc/motd ]]; then cat /etc/motd; fi
if [[ -e $HOME/.motd ]]; then cat $HOME/.motd; fi

