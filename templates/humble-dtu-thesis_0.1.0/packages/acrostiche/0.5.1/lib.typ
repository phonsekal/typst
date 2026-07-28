// State global untuk menyimpan daftar akronim
#let acrostiche-state = state("acrostiche-state", (
  acronyms: (:),
  used: ()
))

#let init-acronyms(defs) = {
  acrostiche-state.update(state => {
    let acrs = state.acronyms
    if type(defs) == dictionary {
      for (k, v) in defs {
        acrs.insert(k, v)
      }
    } else if type(defs) == array {
      for item in defs {
        if type(item) == array and item.len() >= 2 {
          acrs.insert(item.at(0), item.at(1))
        }
      }
    }
    state.acronyms = acrs
    state
  })
}

#let display-def(acr, plural: false) = {
  context {
    let st = acrostiche-state.get()
    if acr in st.acronyms {
      let def = st.acronyms.at(acr)
      if type(def) == dictionary {
        if plural and "plural" in def {
          def.plural
        } else if "long" in def {
          def.long
        } else {
          str(def)
        }
      } else {
        str(def)
      }
    } else {
      text(fill: red, "[" + acr + "?]")
    }
  }
}

#let display-short(acr, plural: false) = {
  if plural {
    acr + "s"
  } else {
    acr
  }
}

#let mark-acr-used(acr) = {
  acrostiche-state.update(state => {
    if not acr in state.used {
      state.used.push(acr)
    }
    state
  })
}

#let acr(acr, plural: false) = {
  context {
    let st = acrostiche-state.get()
    if acr in st.used {
      display-short(acr, plural: plural)
    } else {
      display-def(acr, plural: plural)
      [ (]#display-short(acr, plural: plural)[)]
      mark-acr-used(acr)
    }
  }
}

#let acrpl(acronym) = { acr(acronym, plural: true) }
#let acrfull(acr) = {
  display-def(acr, plural: false)
  [ (]#display-short(acr, plural: false)[)]
  mark-acr-used(acr)
}
#let acrfullpl(acr) = {
  display-def(acr, plural: true)
  [ (]#display-short(acr, plural: true)[)]
  mark-acr-used(acr)
}

#let reset-acronym(acr) = {
  acrostiche-state.update(state => {
    let new-used = ()
    for item in state.used {
      if item != acr {
        new-used.push(item)
      }
    }
    state.used = new-used
    state
  })
}

#let reset-all-acronyms() = {
  acrostiche-state.update(state => {
    state.used = ()
    state
  })
}

// Alias fungsi agar kompatibel dengan penulisan lama
#let acrf(acr) = acrfull(acr)
#let acrfpl(acr) = acrfullpl(acr)
#let racr(acr) = reset-acronym(acr)
#let raacr() = reset-all-acronyms()
#let acresetall = reset-all-acronyms
#let ac = acr
#let acp(acro) = acr(acro, plural: true)
#let acl(acro) = display-def(acro, plural: false)
#let aclp(acro) = display-def(acro, plural: true)
#let acf(acro) = acrf(acro)
#let acfp(acro) = acrfpl(acro)
#let acs(acro) = display-short(acro, plural: false)
#let acsp(acro) = display-short(acro, plural: true)
#let acused(acr) = mark-acr-used(acr)

#let print-index(level: 1, numbering: none, outlined: false, sorted: "") = {
  context {
    let st = acrostiche-state.get()
    let keys = st.acronyms.keys()
    if sorted == "are" or sorted == "asc" {
      keys = keys.sorted()
    }
    for k in keys {
      [ - *#k*: ]
      display-def(k)
      [\ ]
    }
  }
}
